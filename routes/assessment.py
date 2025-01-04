from fastapi import Form, Depends, APIRouter

from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

import crud
from crud import get_db
from models.assessment import InitialText, AssessmentTextModel
from schemas.assessment import InitialTextSchema
from services.assessment import ComplexityAssessmentService
from config import logger, templates
from fastapi import Request

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}


@router.get("/test")
def read_main():
    return {"msg": "Hello World"}


@router.get("/assessment", response_class=HTMLResponse)
def submit_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/assessment", response_class=HTMLResponse)
def create_initial_text(
    initial_text: str = Form(...), db: Session = Depends(get_db)
):
    initial_text_data = InitialTextSchema(text=initial_text)
    initial_text_model = crud.create_model_instance(db=db, model_class=InitialText, model_schema=initial_text_data)
    logger.info(f"Sample text successfully received, ID: {initial_text_model.id}")

    initial_assessment_service = ComplexityAssessmentService(initial_text_model)
    complexity_assessment_data = initial_assessment_service.return_assessment_model_data()
    complexity_assessment_model = crud.create_model_instance(
        db=db, model_class=AssessmentTextModel, model_schema=complexity_assessment_data
    )
    return complexity_assessment_model
