from pymongo import ASCENDING
from pymongo.mongo_client import MongoClient
import config

connection = MongoClient(config.DATABASE_URI)
database = connection['tronci']

users = database['users']
users.ensure_index('github_access_token')

jobs = database['jobs']
jobs.ensure_index([
    ('repo_id', ASCENDING),
    ('created_datetime', ASCENDING),
])
