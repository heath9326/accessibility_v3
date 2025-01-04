import json
from typing import Any

from spacy.lang.ru import Russian
from spacy.tokens import Doc
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Float, Text
from sqlalchemy.orm import relationship

from database import Base
from .schemas import TokenFieldSchema

nlp = Russian()


class InitialText(Base):
    __tablename__ = "initial_text"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    text = Column(String, unique=False, index=True)

    assessments = relationship("AssessmentTextModel", back_populates="initial_text")


class AssessmentTextModel(Base):
    __tablename__ = "complexity_assessment"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    spacy_doc = Column(LargeBinary)
    tokens_data = Column(Text)
    initial_score = Column(Float)

    initial_text_id = Column(Integer, ForeignKey("initial_text.id"))
    initial_text = relationship("InitialText", back_populates="assessments")

    def __init__(self, spacy_doc=None, tokens=None, initial_score=None, initial_text_id=None):
        self.spacy_doc = spacy_doc
        self.tokens = tokens
        self.initial_score = initial_score
        self.initial_text_id = initial_text_id

    @property
    def tokens(self):
        return json.loads(self.tokens_data) if self.tokens_data else []

    @tokens.setter
    def tokens(self, tokens):
        self.tokens_data = json.dumps(tokens) if tokens else None


    @classmethod
    def store_doc(cls, doc: Doc):
        return cls(spacy_doc=doc.to_bytes())

    def retrieve_doc(self):
        # Retrieving the SpaCy Doc object from the field
        retrieved_doc = Doc(nlp.vocab).from_bytes(self.spacy_doc)
        return retrieved_doc

    def retrieve_tokens(self):
        return json.loads(self.tokens_data)
