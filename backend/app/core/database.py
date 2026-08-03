from typing import Optional

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


engine = create_engine(settings.DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db(request: Request):
    db: Session = SessionLocal()
    if hasattr(request, "state"):
        request.state.db = db
    try:
        yield db
    finally:
        db.close()
