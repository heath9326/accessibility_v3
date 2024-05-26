import spacy
from spacy.lang.ru import Russian

from assessement.models import InitialText
from assessement.schemas import TokenFieldSchema, AssessmentTextSchema
from assessement.utils import count_syllables
from simplification.models import SimplificationModel
from spacy.tokens import Token


class SpacyPipeService:
    def __init__(self):
        self.nlp = Russian()
        # self.nlp = spacy.load('ru_core_news_sm')
        self.nlp.add_pipe('sentencizer')

    def process(self, token: Token, keep_pos=True, keep_punct=False):

        entities = {'PROPN'}
        named = False
        memory = []
        mem_case = None
        mem_number = None
        tagged_propn = []

        lemma = token.lemma_
        pos = token.pos_
        if pos in entities:
            if token.dep_ == 'compound':
                pass
            if token.ent_iob_ != 'O':
                named = True
                if not mem_case:
                    mem_case = token._.case
                    mem_number = token._.number
                if token._.case == mem_case and token._.number == mem_number:
                    tagged_propn.append(f'{lemma}_{pos}')
            else:
                if not named:
                    tagged_propn.append(f'{lemma}_{pos}')

        return tagged_propn


class ComplexityAssessmentService:
    def __init__(self, text_model: InitialText | SimplificationModel):
        self.spacy_pipe_service = SpacyPipeService()

        self.text_model = text_model
        if isinstance(self.text_model, InitialText):
            self.doc = self.spacy_pipe_service.nlp(self.text_model.text)
        else:
            self.doc = self.spacy_pipe_service.nlp(self.text_model.simplified_text)

        token_list = [token for token in self.doc]
        print(token_list)

    def calculate_sentences(self):
        return len([sent.text for sent in self.doc.sents])

    def calculate_words(self):
        return len([token for token in self.doc if token.is_alpha])

    def calculate_syllables(self):
        syllable_count = 0
        for token in self.doc:
            syllable_count += count_syllables(token.text)
        return syllable_count

    def _create_tokens_field(self):
        token_fields: list[TokenFieldSchema] = []
        for token in self.doc:
            syllables_count = count_syllables(token.text)
            is_to_simplify = True if syllables_count > 4 else False
            token_fields.append(
                TokenFieldSchema(
                    text=token.text,
                    syllables_count=syllables_count,
                    is_to_simplify=is_to_simplify
                )
            )
        return token_fields

    def calculate_complexity(self):
        sentences = self.calculate_sentences()
        words = self.calculate_words()
        syllables = self.calculate_syllables()

        # Calculate ASL (average sentence length)
        ASL = words / sentences
        # Calculate ASW (average number of syllables per word)
        ASW = syllables / words

        # Calculate complexity index
        self.complexity_score = 206.835 - 1.52 * ASL - 65.14 * ASW
        return self.complexity_score

    def return_assessment_model_data(self):
        return (
            AssessmentTextSchema(
                initial_text_id=self.text_model.id,
                spacy_doc=self.doc.to_bytes(),
                tokens=self._create_tokens_field(),
                initial_score=self.calculate_complexity()
            )
        )

