from spacy.lang.ru import Russian

from assessement.models import InitialText
from assessement.schemas import TokenFieldSchema, AssessmentTextSchema

nlp = Russian()
nlp.add_pipe('sentencizer')


class ComplexityAssessmentService:
    def __init__(self, initial_text_model: InitialText):
        self.initial_text_model = initial_text_model
        self.doc = nlp(self.initial_text_model.text)

    def _calculate_sentences(self):
        return len([sent.text for sent in self.doc.sents])

    def _calculate_words(self):
        return len([token for token in self.doc if token.is_alpha])

    @staticmethod
    def count_syllables(word):
        # Get vowel sounds in the word
        last_letter = [*word][-1]
        vowels = ["а", "у", "о", "и", "э", "ы", "е", "ё", "ю", "я"]
        num_syllables = 0
        prev_char = ''

        for char in word:
            if char.lower() in vowels and prev_char not in vowels:
                num_syllables += 1
            elif char == last_letter and char in vowels:
                num_syllables += 1
            prev_char = char
        return num_syllables

    def _calculate_syllables(self):
        syllable_count = 0
        for token in self.doc:
            syllable_count += self.count_syllables(token.text)
        return syllable_count

    def _create_tokens_field(self):
        token_fields: list[TokenFieldSchema] = []
        for token in self.doc:
            syllables_count = self.count_syllables(token.text)
            is_to_simplify = True if syllables_count > 4 else False
            token_fields.append(
                TokenFieldSchema(
                    text=token.text,
                    syllables_count=syllables_count,
                    is_to_simplify=is_to_simplify
                )
            )
        return token_fields

    def _calculate_complexity(self):
        sentences = self._calculate_sentences()
        words = self._calculate_words()
        syllables = self._calculate_syllables()

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
                initial_text_id=self.initial_text_model.id,
                spacy_doc=self.doc.to_bytes(),
                tokens=self._create_tokens_field(),
                initial_score=self._calculate_complexity()
            )
        )

