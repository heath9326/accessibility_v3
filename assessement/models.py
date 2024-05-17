from typing import Any

from spacy.lang.ru import Russian
from spacy.tokens import Doc, Token
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base
nlp = Russian()


class InitialText(Base):
    __tablename__ = "initial_text"

    id = Column(Integer, primary_key=True)
    text = Column(String, unique=False, index=True)

    # items = relationship("Item", back_populates="owner")


class TokenField(Base):
    token = Token
    syllables_count = int
    is_to_simplify: bool


class AssessmentTextModel(Base):
    initial_text: InitialText
    spacy_doc: Any
    tokenized_text: list[TokenField]
    initial_score: float

    @classmethod
    def store_doc(cls, doc: Doc):
        return cls(spacy_doc=doc.to_bytes())

    def retrieve_doc(self):
        # Retrieving the SpaCy Doc object from the field
        retrieved_doc = Doc(nlp.vocab).from_bytes(self.spacy_doc)
        return retrieved_doc

    class Config:
        arbitrary_types_allowed = True