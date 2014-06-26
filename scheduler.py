from apscheduler.scheduler import Scheduler
from database import connection
import config

scheduler = Scheduler({
    'apscheduler.jobstore.default.class': 'apscheduler.jobstores.mongodb_store:MongoDBJobStore',
    'apscheduler.jobstore.default.database': config.DATABASE_NAME,
    'apscheduler.jobstore.default.collection': 'aps_jobs',
    'apscheduler.jobstore.default.connection': connection,
    'apscheduler.misfire_grace_time': 600, # 10 minutes
    'apscheduler.coalesce': True, # Roll several pending executions of jobs into one
})
