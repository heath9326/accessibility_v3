from typing import Optional, Any
from spacy.lang.ru import Russian
from pydantic import BaseModel
import spacy
from spacy.tokens import Doc, Token
nlp = Russian()


class InitialText(BaseModel):
    text: str


class TokenField(BaseModel):
    token: Token
    syllables_count: int
    is_to_simplify: bool

    class Config:
        arbitrary_types_allowed = True


class AssessmentTextModel(BaseModel):
    initial_text: InitialText
    spacy_doc: Any
    # tokenized_text: list[TokenField]
    # initial_score: float

    @classmethod
    def store_doc(cls, doc: Doc):
        return cls(spacy_doc=doc.to_bytes())

    def retrieve_doc(self):
        # Retrieving the SpaCy Doc object from the field
        retrieved_doc = Doc(nlp.vocab).from_bytes(self.spacy_doc)
        return retrieved_doc

    class Config:
        arbitrary_types_allowed = True


class SimplificationDoc(BaseModel):
    assessment_model: AssessmentTextModel
    result_score: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True

