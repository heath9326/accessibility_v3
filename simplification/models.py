import json

from sqlalchemy import ForeignKey, Column, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from assessement.models import AssessmentTextModel


class SimplificationModel(AssessmentTextModel):
    __tablename__ = "simplification"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(ForeignKey("complexity_assessment.id"), primary_key=True)
    tokens_data = Column(Text)
    simplified_text: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "simplification",
    }

    def __init__(self,
                 spacy_doc=None,
                 tokens=None,
                 initial_score=None,
                 initial_text_id=None,
                 simplified_text=None
                 ):
        super().__init__(spacy_doc, tokens, initial_score, initial_text_id)
        self.spacy_doc = spacy_doc
        self.tokens = tokens
        self.initial_score = initial_score
        self.initial_text_id = initial_text_id
        self.simplified_text = simplified_text

    @hybrid_property
    def tokens(self):
        return json.loads(self.tokens_data) if self.tokens_data else []

    @tokens.setter
    def tokens(self, tokens):
        self.tokens_data = json.dumps(tokens) if tokens else None