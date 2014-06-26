from bson.objectid import ObjectId
from flask import Flask, session, redirect, url_for
from flask.globals import g, request
from flask.templating import render_template
from flask_github import GitHub
import config
import logging
import views


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s]: %(levelname)s : %(message)s'
)


# Settings -----------------------------------------------------------------------------------------

# Flask
app = Flask(__name__)
app.config.from_object(config)

# GitHub
github = GitHub(app)


# App ----------------------------------------------------------------------------------------------

@app.before_request
def before_request():
    from travispy import TravisPy
    from database import users

    g.user = None
    g.travispy = None

    if 'user_id' in session:
        g.user = users.find_one({'_id': ObjectId(session['user_id'])})

    if g.user is not None:
        g.travispy = TravisPy.github_auth(g.user['github_access_token'])


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login/')
def login():
    return github.authorize(config.GITHUB_SCOPE)


@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    user = g.user
    if user:
        return redirect(url_for('repositories'))
    else:
        return render_template('index.html')


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    from database import users

    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = users.find_one({'github_access_token': access_token})
    if user is None:
        user = {'github_access_token': access_token}
        user_id = users.insert(user)
    else:
        user_id = user['_id']

    session['user_id'] = str(user_id)
    return redirect(url_for('index'))


@github.access_token_getter
def get_access_token():
    user = g.user
    if user is not None:
        return user.github_access_token


app.add_url_rule('/repositories/', view_func=views.RepositoriesAPI.as_view('repositories'))
app.add_url_rule('/jobs/<int:repo_id>/', view_func=views.JobsAPI.as_view('jobs'))
app.add_url_rule('/jobs/<int:repo_id>/new/', view_func=views.NewJobAPI.as_view('new_job'))
app.add_url_rule('/jobs/<int:repo_id>/delete/<job_id>/', view_func=views.DeleteJobAPI.as_view('delete_job'))


#===================================================================================================
# __main__
#===================================================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0')
