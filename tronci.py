import logging
from urlparse import parse_qsl

from flask import Flask, jsonify, request
from flask.templating import render_template
import requests

import config


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s]: %(levelname)s : %(message)s'
)


# Settings -----------------------------------------------------------------------------------------

# Flask
app = Flask(__name__)
app.config.from_object(config)


# App ----------------------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/job/')
def job():
    return render_template('job.html')


@app.route('/cron-template/')
def cron_template():
    return render_template('cron_template.html')


@app.route('/auth/github', methods=['POST'])
def github(*args, **kwargs):
    params = {
        'client_id': request.json['clientId'],
        'client_secret': app.config['GITHUB_CLIENT_SECRET'],
        'code': request.json['code'],
        'redirect_uri': request.json['redirectUri'],
    }

    # Exchange authorization code for access token.
    response = requests.get('https://github.com/login/oauth/access_token', params=params)
    access_token = dict(parse_qsl(response.text))
    headers = {'User-Agent': 'Satellizer'}

    # Retrieve information about the current user.
    response = requests.get('https://api.github.com/user', params=access_token, headers=headers)
    profile = response.json()

#     # (optional) Link accounts.
#     if request.headers.get('Authorization'):
#         user = User.query.filter_by(github=profile['id']).first()
#         if user:
#             response = jsonify(message='There is already a GitHub account that belongs to you')
#             response.status_code = 409
#             return response
#
#         payload = parse_token(request)
#
#         user = User.query.filter_by(id=payload['sub']).first()
#         if not user:
#             response = jsonify(message='User not found')
#             response.status_code = 400
#             return response
#
#         user.github = profile['id']
#         user.display_name = display_name or profile['name']
#         db.session.commit()
#         token = create_token(user)
#         return jsonify(token=token)
#
#     # Create a new account or return an existing one.
#     user = User.query.filter_by(github=profile['id']).first()
#     if user:
#         token = create_token(user)
#         return jsonify(token=token)
#
#     u = User(github=profile['id'], display_name=profile['name'])
#     db.session.add(u)
#     db.session.commit()
#     token = create_token(u)
    return jsonify(token=access_token['access_token'])


# @app.before_request
# def before_request():
#     from travispy import TravisPy
#     from database import users
#
#     g.user = None
#     g.travispy = None
#
#     if 'user_id' in session:
#         g.user = users.find_one({'_id': ObjectId(session['user_id'])})
#
#     if g.user is not None:
#         g.travispy = TravisPy.github_auth(g.user['github_access_token'])
#
#
# app.add_url_rule('/repos/', view_func=RepositoriesAPI.as_view('repos'))
# app.add_url_rule('/repos/<int:repo_id>/jobs/', view_func=JobsView.as_view('jobs'))
# app.add_url_rule('/repos/<int:repo_id>/jobs/<int:job_id>/', view_func=JobsAPI.as_view('jobs_api'))


#===================================================================================================
# __main__
#===================================================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0')
