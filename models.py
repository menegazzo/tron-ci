from database import Base, engine
from scheduler import scheduler # @UnusedImport
from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, Table
from sqlalchemy.types import DateTime


#===================================================================================================
# User
#===================================================================================================
class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    github_access_token = Column(String(50), unique=True)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


#===================================================================================================
# APSJob
#===================================================================================================
class APSJob(Base):

    __table__ = Table('apscheduler_jobs', Base.metadata, autoload=True, autoload_with=engine)

    job = relationship('Job', uselist=False, backref='aps_job')


#===================================================================================================
# Job
#===================================================================================================
class Job(Base):

    __tablename__ = 'jobs'

    id = Column(Integer, Sequence('job_id_seq'), primary_key=True)
    aps_job_id = Column(Integer, ForeignKey('apscheduler_jobs.id'))
    repository_id = Column(Integer)
    created_datetime = Column(DateTime)

    @hybrid_property
    def created(self):
        return self.created_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        fields = dict((field.name, str(field)) for field in self.aps_job.trigger.fields)
        return '%(minute)s %(hour)s %(day_of_week)s %(week)s %(day)s %(month)s' % fields
