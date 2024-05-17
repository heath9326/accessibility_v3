from typing import Any, Optional

from fastapi import Body
from pydantic import BaseModel
from spacy.tokens import Token, Doc

from assessement import Base
from assessement.models import nlp


class InitialTextSchema(BaseModel):
    text: str

    class Config:
        orm_mode = True


# class TokenField(BaseModel):
#     token: Token
#     syllables_count: int
#     is_to_simplify: bool
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
class AssessmentTextSchema(BaseModel):
    initial_text: InitialTextSchema
    spacy_doc: Any
    # tokenized_text: list[TokenField]
    # initial_score: float
#
#     @classmethod
#     def store_doc(cls, doc: Doc):
#         return cls(spacy_doc=doc.to_bytes())
#
#     def retrieve_doc(self):
#         # Retrieving the SpaCy Doc object from the field
#         retrieved_doc = Doc(nlp.vocab).from_bytes(self.spacy_doc)
#         return retrieved_doc
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# class SimplificationDoc(BaseModel):
#     assessment_model: AssessmentTextModel
#     result_score: Optional[float] = None
#
#     class Config:
#         arbitrary_types_allowed = True
