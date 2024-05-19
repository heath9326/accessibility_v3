from typing import Optional

from assessement.schemas import TokenFieldSchema, AssessmentTextSchema


class TokenFieldExtendedSchema(TokenFieldSchema):
    tag: Optional[list[str]] = None
    synonyms: Optional[list[tuple]] = None

    class Config:
        arbitrary_types_allowed = True


class SimplificationTextSchema(AssessmentTextSchema):
    tokens: list[TokenFieldExtendedSchema]
    simplified_text: str
