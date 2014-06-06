from flask import Flask, render_template_string, session, redirect, url_for, render_template
from flask.globals import g, request
from flask_github import GitHub
from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from travispy import TravisPy
import config

# Flask
app = Flask(__name__)
app.config.from_object(config)

# GitHub
github = GitHub(app)

# SQLAlchemy
engine = create_engine(config.DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(engine, autoflush=False, autocommit=False))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(engine)


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    github_access_token = Column(String(50), unique=True)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


    def repr(self):
        return "<User(id=%d, github_access_token=%s, travis_access_token=%s)>" % (
            self.id,
            self.github_access_token,
            self.travis_access_token,
        )


# App ----------------------------------------------------------------------------------------------

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/')
def index():
    user = g.user
    if user:
        travispy = TravisPy.github_auth(user.github_access_token)
        github_user = travispy.user()
        repos = travispy.repos(member=github_user.login, active=True)
        return render_template('repositories.html', user=github_user, repos=repos)
    else:
        return render_template_string('Hello! <a href="{{ url_for("login") }}">Login</a>')


@app.route('/login')
def login():
    return github.authorize(config.GITHUB_SCOPE)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def get_user():
    return str(github.get('user'))


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
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


#===================================================================================================
# __main__
#===================================================================================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
