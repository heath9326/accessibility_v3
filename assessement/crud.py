from typing import Type

from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_model_instance(db: Session, model_class: Type[models.Model], model_schema: Type[schemas]):
    db_item = model_class(**model_schema.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_model_instance(db: Session, model_class: Type[models.Model], **kwargs):
    """
    Fetch a single InitialText item by its ID.

    Args:
        db (Session): The database session.
        **kwargs: dynamic class number of kwargs

    Returns:
        Instance of model_class or None: The retrieved model_class item, or None if not found.
    """
    return db.query(model_class).filter_by(**kwargs).first()
