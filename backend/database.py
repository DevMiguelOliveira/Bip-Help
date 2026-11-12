from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# A URL segue o formato: postgresql://usuario:senha@host:porta/banco
SQLALCHEMY_DATABASE_URL = Path("/etc/bipmanager/database_url").read_text().strip()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
