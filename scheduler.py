from apscheduler.scheduler import Scheduler
from database import connection

scheduler = Scheduler({
    'apscheduler.jobstore.default.class': 'apscheduler.jobstores.mongodb_store:MongoDBJobStore',
    'apscheduler.jobstore.default.database': 'tronci',
    'apscheduler.jobstore.default.collection': 'aps_jobs',
    'apscheduler.jobstore.default.connection': connection,
    'apscheduler.misfire_grace_time': 600, # 10 minutes
    'apscheduler.coalesce': True, # Roll several pending executions of jobs into one
})
