from apscheduler.scheduler import Scheduler
from database import engine, metadata

scheduler = Scheduler({
    'apscheduler.jobstore.default.class': 'apscheduler.jobstores.sqlalchemy_store:SQLAlchemyJobStore',
    'apscheduler.jobstore.default.engine': engine,
    'apscheduler.jobstore.default.metadata': metadata,
    'apscheduler.misfire_grace_time': 600, # 10 minutes
    'apscheduler.coalesce': True, # Roll several pending executions of jobs into one
})
