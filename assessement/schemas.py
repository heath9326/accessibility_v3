from typing import Any, Optional

from pydantic import BaseModel
from spacy.tokens import Token


class InitialTextSchema(BaseModel):
    text: str

    class Config:
        from_attributes = True


class TokenFieldSchema(BaseModel):
    text: str
    syllables_count: int
    is_to_simplify: bool

    class Config:
        arbitrary_types_allowed = True


class AssessmentTextSchema(BaseModel):
    initial_text_id: Optional[int] = None  # FIXME remove optional after testing the script
    spacy_doc: Any
    tokens: list[TokenFieldSchema]
    initial_score: float
#
#     @classmethod
#     def store_doc(cls, doc: Doc):
#         return cls(spacy_doc=doc.to_bytes())
#
    # def retrieve_doc(self):
    #     # Retrieving the SpaCy Doc object from the field
    #     retrieved_doc = Doc(nlp.vocab).from_bytes(self.spacy_doc)
    #     return retrieved_doc
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
