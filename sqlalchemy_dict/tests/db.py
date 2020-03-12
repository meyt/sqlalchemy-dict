from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_dict import BaseModel

metadata = MetaData()
DeclarativeBase = declarative_base(cls=BaseModel, metadata=metadata)
