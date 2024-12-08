from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_initial_text_item(db: Session, initial_text: schemas.InitialTextSchema):
    db_item = models.InitialText(**initial_text.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_assessment_model_item(db: Session, assessment_model: schemas.AssessmentTextSchema):
    db_item = models.AssessmentTextModel(**assessment_model.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
