from typing import Optional

from assessement.schemas import TokenFieldSchema, AssessmentTextSchema


class TokenFieldExtendedSchema(TokenFieldSchema):
    tag: Optional[str] = None
    synonyms: list[str] = None

    class Config:
        arbitrary_types_allowed = True


class SimplificationTextSchema(AssessmentTextSchema):
    tokens: list[TokenFieldExtendedSchema]
    simplified_text: str
