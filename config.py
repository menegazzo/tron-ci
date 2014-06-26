import os


# Flask variables
DATABASE_NAME = os.environ['DATABASE_NAME']
DATABASE_URI = os.environ['DATABASE_URI']
DEBUG = True
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = 'DVsItM4vYgvRZd6G/htFOR/+hGgOjCPPrjdg+6hFZQ6E93r9aivYXyYWC3DnaHU48/0qZtAFJZJB\n0cv57iAwmg==\n'

# GitHub variables
GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
GITHUB_CALLBACK_URL = os.environ['GITHUB_CALLBACK_URL']
GITHUB_SCOPE = 'read:org, repo:status, repo_deployment, user:email, write:repo_hook'
