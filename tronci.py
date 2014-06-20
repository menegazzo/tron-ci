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

@app.teardown_appcontext
def shutdown_session(exception=None):
    from database import db_session
    db_session.remove()


@app.before_request
def before_request():
    from models import User
    from travispy import TravisPy

    g.user = None
    if 'user_id' in session:
        g.user = user = User.query.get(session['user_id'])
        g.travispy = TravisPy.github_auth(user.github_access_token)


@app.after_request
def after_request(response):
    from database import db_session
    db_session.remove()
    return response


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


@app.route('/github-callback/')
@github.authorized_handler
def authorized(access_token):
    from database import db_session
    from models import User

    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db_session.add(user)

    db_session.commit()

    session['user_id'] = user.id
    return redirect(url_for('index'))


@github.access_token_getter
def get_access_token():
    user = g.user
    if user is not None:
        return user.github_access_token


app.add_url_rule('/repositories/', view_func=views.RepositoriesAPI.as_view('repositories'))
app.add_url_rule('/jobs/<int:repo_id>/', view_func=views.JobsAPI.as_view('jobs'))
app.add_url_rule('/jobs/<int:repo_id>/new/', view_func=views.NewJobAPI.as_view('new_job'))
app.add_url_rule('/jobs/<int:repo_id>/delete/<int:job_id>/', view_func=views.DeleteJobAPI.as_view('delete_job'))


#===================================================================================================
# __main__
#===================================================================================================
if __name__ == '__main__':
    from database import init_db
    init_db()
    app.run(debug=True)
