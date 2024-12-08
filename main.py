from fastapi import Depends, FastAPI
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from assessement import crud, models
from assessement.crud import get_db
from assessement.database import engine
from assessement.models import InitialText, AssessmentTextModel
from assessement.schemas import InitialTextSchema
from assessement.services import ComplexityAssessmentService
from config import logger, templates, app
from simplification.models import SimplificationModel
from simplification.services import SimplificationService


models.Base.metadata.create_all(bind=engine)

# Dependency


@app.get("/", response_class=HTMLResponse)
async def submit_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
def create_initial_text(
    initial_text: str = Form(...), db: Session = Depends(get_db)
):
    initial_test_instance = crud.create_initial_text_item(db=db, initial_text=initial_text)
    processed_text = initial_test_instance

    logger.info("Processing sample text № {i}.")
    initial_text_data = InitialTextSchema(text=sample_text)
    initial_text_model = InitialText(**initial_text_data.model_dump())

    initial_assessment_service = ComplexityAssessmentService(initial_text_model)
    complexity_assessment_data = initial_assessment_service.return_assessment_model_data()

    number_of_words = initial_assessment_service.calculate_words()
    logger.info(f"Number of words: {number_of_words}")

    number_of_sentences = initial_assessment_service.calculate_sentences()
    logger.info(f"Number of sentences: {number_of_sentences}")

    number_of_syllables = initial_assessment_service.calculate_syllables()
    logger.info(f"Number of syllables: {number_of_syllables}")

    complexity = initial_assessment_service.calculate_complexity()
    logger.info(f"Initial Complexity score: {complexity}")

    complexity_assessment_model = AssessmentTextModel(**complexity_assessment_data.model_dump())

    simplification_service = SimplificationService(complexity_assessment_model)
    simplification_model_data = simplification_service.return_simplification_model_data()
    simplification_model = SimplificationModel(**simplification_model_data.model_dump())

    logger.info(f"Simplified text of sample text # {i}:\n"
          f"{simplification_model.simplified_text}")

    final_assessment_service = ComplexityAssessmentService(simplification_model)
    number_of_words = final_assessment_service.calculate_words()
    logger.info(f"Final Number of words: {number_of_words}")

    number_of_sentences = final_assessment_service.calculate_sentences()
    logger.info(f"Final Number of sentences: {number_of_sentences}")

    number_of_syllables = final_assessment_service.calculate_syllables()
    logger.info(f"Final Number of syllables: {number_of_syllables}")

    final_complexity_score = final_assessment_service.calculate_complexity()
    return {"initial_text": initial_text, "simplified_text": processed_text}