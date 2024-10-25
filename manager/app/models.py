
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

from enum import Enum

# Configuração do SQLite
DATABASE_URL = "sqlite:////data/monitor.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo para a tabela Status
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
    type       = Column(String)
    message    = Column(String)
    timestamp  = Column(DateTime, default=datetime.now())


class File(Base):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    session_id   = Column(String,)
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

if __name__ == "__main__":

    Base.metadata.create_all(bind=engine)