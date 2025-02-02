
# ORM Imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Pydantic for smarter API Typing
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

from enum import Enum

# Configuração do SQLite
DATABASE_URL = "sqlite:////data/monitor.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==================================
# ORM Models
# ==================================
class Status(Base):
    __tablename__ = "status"

    session_id = Column(String, primary_key=True, index=True)
    app_name = Column(String)
    start = Column(DateTime, default=datetime.now())
    end = Column(DateTime, nullable=True)
    status = Column(String)


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    session_id = Column(String, index=True)
    app_name   = Column(String)
    level      = Column(String)
    message    = Column(String)
    timestamp  = Column(DateTime, default=datetime.now())


class File(Base):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    session_id   = Column(String, )
    organization = Column(String, )
    project      = Column(String, )
    filename     = Column(String, )
    upload_ts    = Column(DateTime, default=datetime.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================================
# Pydantic Models
# ==================================
class LogModel(BaseModel):
    id         : Optional[int] = None
    session_id : str
    app_name   : str
    level      : Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    message    : str
    timestamp  : Optional[datetime] = None # The database already handles timestamp default value

    class Config:
        from_attributes = True

class StatusModel(BaseModel):
    session_id : str
    app_name   : str
    start      : Optional[datetime] = None
    end        : Optional[datetime] = None
    status     : str

    class Config:
        from_attributes = True

class StatusUpdateModel(BaseModel):
    session_id: str
    status: str
    start: Optional[datetime] = None
    end:    Optional[datetime] = None

class FileModel(BaseModel):
    id: Optional[int] = None
    session_id: str
    organization: str
    project: str
    filename: str = None
    upload_ts: Optional[datetime] = None

    class Config:
        from_attributes = True


class SlackMessageModel(BaseModel):
    blocks: list[dict]


if __name__ == "__main__":

    Base.metadata.create_all(bind=engine)