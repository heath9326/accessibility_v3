from fastapi import Depends
from fastapi import Request, Form
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def submit_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
def create_initial_text(
    initial_text: str = Form(...), db: Session = Depends(get_db)
):
    logger.info("Processing sample text № {i}.")
    initial_text_data = InitialTextSchema(text=initial_text)
    initial_text_model = crud.create_model_instance(db=db, model_class=InitialText, model_schema=initial_text_data)

    initial_assessment_service = ComplexityAssessmentService(initial_text_model)
    complexity_assessment_data = initial_assessment_service.return_assessment_model_data()
    complexity_assessment_model = crud.create_model_instance(
        db=db, model_class=AssessmentTextModel, model_schema=complexity_assessment_data
    )
    return complexity_assessment_model


@app.post("/simplify", response_class=HTMLResponse)
def create_initial_text(
        complexity_assessment_model_id: int = Form(...), db: Session = Depends(get_db)
):
    complexity_assessment_model = crud.get_model_instance(
        db=db, model_class=AssessmentTextModel, **{"id": complexity_assessment_model_id}
    )

    simplification_service = SimplificationService(complexity_assessment_model)
    simplification_model_data = simplification_service.return_simplification_model_data()
    simplification_model = crud.create_model_instance(
        db=db, model_class=SimplificationModel, model_schema=simplification_model_data
    )

    final_assessment_service = ComplexityAssessmentService(simplification_model)
    final_complexity_score = final_assessment_service.calculate_complexity()
    return {
        "initial_complexity_score": simplification_model.initial_score,
        "final_complexity_score": final_complexity_score,
        "simplified_text": simplification_model.simplified_text
    }
