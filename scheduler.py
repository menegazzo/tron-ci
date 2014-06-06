from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
from apscheduler.scheduler import Scheduler
from database import Base, engine
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer



job_store = SQLAlchemyJobStore(engine=engine, tablename='jobs')



class Job(Base):

    __table__ = job_store.jobs_t

    repo_id = Column(Integer)
    created_by = 



scheduler = Scheduler()
scheduler.add_jobstore(job_store, 'db')


@scheduler.interval_schedule(minutes=1)
def timed_job():
    print 'This job prints every 1 minute.'


scheduler.start()
while True:
    pass
