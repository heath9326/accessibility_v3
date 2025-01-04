from fastapi import Form, Depends, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

import crud
from crud import get_db
from assessement.models import AssessmentTextModel
from assessement.services import ComplexityAssessmentService

from simplification.models import SimplificationModel
from simplification.services import SimplificationService

router = APIRouter()


@router.post("/simplify", response_class=HTMLResponse)
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
