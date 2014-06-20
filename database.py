from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData
import config


engine = create_engine(config.DATABASE_URI, echo=False)
metadata = MetaData(engine)
db_session = scoped_session(sessionmaker(engine, autoflush=False, autocommit=False))

Base = declarative_base(engine, metadata)
Base.query = db_session.query_property()


def init_db():
    import models # @UnusedImport
    Base.metadata.create_all(engine)
