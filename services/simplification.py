import os
import sys
import zipfile

import gensim
import pymorphy2
import wget
from spacy.tokens import Token
from ufal.udpipe import Model, Pipeline

from models.assessment import AssessmentTextModel
from services.assessment import SpacyPipeService
from utils import count_syllables
from config import settings
from schemas.simplification import SimplificationTextSchema, TokenFieldExtendedSchema


class ModelService:
    filename: str
    filepath: str
    download_url: str

    def __init__(self, filename: str = None, filepath: str = None, download_url: str = None):
        self.filename = filename
        self.filepath = filepath
        self.download_url = download_url


class UdPipeModelService(ModelService):
    def __init__(self):
        super(UdPipeModelService, self).__init__(
            filename='udpipe_syntagrus.model',
            filepath=r'C:\Users\Евгения\PycharmProjects\models',
            download_url='https://rusvectores.org/static/models/udpipe_syntagrus.model'
        )
        self.model = self._get_model()
        self.process_pipeline = Pipeline(self.model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

    def _get_model(self):
        full_path = os.path.join(self.filepath, self.filename)

        if not os.path.isfile(full_path):
            print('UDPipe model not found. Downloading...', file=sys.stderr)
            wget.download(self.download_url)

        print('\nLoading the model...', file=sys.stderr)
        model = Model.load(full_path)

        return model

    def process(self, word: str, keep_pos=True, keep_punct=False):
        entities = {'PROPN'}
        named = False
        memory = []
        mem_case = None
        mem_number = None
        tagged_propn = []

        # обрабатываем текст, получаем результат в формате conllu:
        processed = self.process_pipeline.process(word)

        # пропускаем строки со служебной информацией:
        content = [l for l in processed.split('\n') if not l.startswith('#')]

        # извлекаем из обработанного текста леммы, тэги и морфологические характеристики
        tagged = [w.split('\t') for w in content if w]

        for t in tagged:
            if len(t) != 10:
                continue
            (word_id, token, lemma, pos, xpos, feats, head, deprel, deps, misc) = t
            if not lemma or not token:
                continue
            if pos in entities:
                if '|' not in feats:
                    tagged_propn.append('%s_%s' % (lemma, pos))
                    continue
                morph = {el.split('=')[0]: el.split('=')[1] for el in feats.split('|')}
                if 'Case' not in morph or 'Number' not in morph:
                    tagged_propn.append('%s_%s' % (lemma, pos))
                    continue
                if not named:
                    named = True
                    mem_case = morph['Case']
                    mem_number = morph['Number']
                if morph['Case'] == mem_case and morph['Number'] == mem_number:
                    memory.append(lemma)
                    if 'SpacesAfter=\\n' in misc or 'SpacesAfter=\s\\n' in misc:
                        named = False
                        past_lemma = '::'.join(memory)
                        memory = []
                        tagged_propn.append(past_lemma + '_PROPN ')
                else:
                    named = False
                    past_lemma = '::'.join(memory)
                    memory = []
                    tagged_propn.append(past_lemma + '_PROPN ')
                    tagged_propn.append('%s_%s' % (lemma, pos))
            else:
                if not named:
                    if pos == 'NUM' and token.isdigit():  # Заменяем числа на xxxxx той же длины
                        lemma = self._num_replace(token)
                    tagged_propn.append('%s_%s' % (lemma, pos))
                else:
                    named = False
                    past_lemma = '::'.join(memory)
                    memory = []
                    tagged_propn.append(past_lemma + '_PROPN ')
                    tagged_propn.append('%s_%s' % (lemma, pos))

        if not keep_punct:
            tagged_propn = [word for word in tagged_propn if word.split('_')[1] != 'PUNCT']
        if not keep_pos:
            tagged_propn = [word.split('_')[0] for word in tagged_propn]
        return tagged_propn

    def _num_replace(self, token):
        pass

    # def process_text(self, words: list[str]):
    #     print('Processing input...', file=sys.stderr)
    #     tagged = []
    #     for word in words:
    #         # line = unify_sym(line.strip()) # здесь могла бы быть ваша функция очистки текста
    #         output = self._process(process_pipeline, text=word)
    #         tagged_line = ' '.join(output)
    #         tagged.append(tagged_line)
    #     return tagged


class VectorModelService(ModelService):
    def __init__(self):
        super(VectorModelService, self).__init__(
            filename='model.bin',
            filepath=r'C:\Users\Евгения\PycharmProjects\models',
            download_url='http://vectors.nlpl.eu/repository/20/180.zip'
        )
        self.model = self._get_model()

    def _get_model(self):
        full_path = os.path.join(self.filepath, self.filename)

        if not os.path.isfile(full_path):
            print('UDPipe model not found. Downloading...', file=sys.stderr)
            wget.download(self.download_url)
            archive_file = self.download_url.split('/')[-1]

            achive_path = os.path.join(self.filepath, archive_file)
            with zipfile.ZipFile(achive_path, 'r') as archive:
                stream = archive.open('model.bin')
                model = gensim.models.KeyedVectors.load_word2vec_format(stream, binary=True)
                return model

        model = gensim.models.KeyedVectors.load_word2vec_format(full_path, binary=True)
        return model

    def process_synonyms(self, preprocessed_text):
        for word in preprocessed_text:
            # есть ли слово в модели? Может быть, и нет
            if word in self.model:
                print(word)
                self.get_synonyms(word)
            else:
                # Увы!
                print(word + ' is not present in the model')

    def filter_by_pos(self, token_tag: str, synonym: str):
        token_pos = token_tag.split("_")[-1]
        synonym_pos = synonym.split("_")[-1]
        return True if token_pos == synonym_pos else False

    def is_not_antonym(self, token_tag, synonym_tag):
        antonyms = [antonym_tag for antonym_tag, closeness_index in self.model.most_similar(negative=[token_tag], topn=10)]
        return False if synonym_tag in antonyms else True

    def is_not_same_root(self, word1, word2):
        # Вычисление косинусного расстояния между векторами
        similarity = self.model.similarity(word1, word2)

        # Порог для схожести слов
        threshold = 0.6
        if similarity >= threshold:
            return False
        else:
            return True

    def is_lower_complexity(self, synonym_tag):
        return True if count_syllables(synonym_tag) < settings.word_complexity_index else False

    def get_synonyms(self, token_tags: list):
        if not token_tags:
            return []

        for token_tag in token_tags:
            if token_tag not in self.model:
                return []
        # выдаем 10 ближайших соседей слова:
        synonyms: list[tuple] = []

        token_tag = token_tags[0]
        for synonym_tag, closeness_index in self.model.most_similar(positive=[token_tag], topn=10):
            flags = {
                "is_antonym": self.is_not_antonym(token_tag, synonym_tag),
                "is_lower_complexity": self.is_lower_complexity(synonym_tag),
                "is_same_pos": self.filter_by_pos(token_tag, synonym_tag),
                "is_not_same_root": self.is_not_same_root(token_tag, synonym_tag)
            }
            if all(flags.values()):
                synonyms.append((synonym_tag, closeness_index))
        return synonyms
        # print('\n')

    def print_synonyms_relative_cosine_similarity(self, preprocessed_word: str, synonym):
        topn = 5  # Number of closest synonyms to retrieve
        similarity_index = self.model.relative_cosine_similarity(wa=preprocessed_word, wb=synonym, topn=topn)
        # print(f"Similarity index for {synonym}: {similarity_index}")


class SimplificationService:

    def __init__(self, assessment_model: AssessmentTextModel):
        self.assessment_model = assessment_model
        self.udpipe_model_service = UdPipeModelService()
        self.spacy_pipe_service = SpacyPipeService()
        self.word2vec_model_service = VectorModelService()
        self.morph = pymorphy2.MorphAnalyzer()

    @property
    def doc(self):
        return self.assessment_model.retrieve_doc()

    @property
    def token_list(self):
        return [token for token in self.doc]

    @property
    def synonym_pipeline(self):
        return [
            self._adjust_word_case,
            self._adjust_word_plurality,
            self._adjust_word_capitalization
        ]

    @property
    def token_fields(self):
        return self._create_tokens_field()

    def _create_tokens_field(self):
        token_fields: list[TokenFieldExtendedSchema] = []
        for i, token_field in enumerate(self.assessment_model.tokens):
            token_text = token_field['text']
            token_tag = self.udpipe_model_service.process(token_field['text'])
            token_fields.append(
                TokenFieldExtendedSchema(
                    text=token_text,
                    syllables_count=token_field['syllables_count'],
                    is_to_simplify=token_field['is_to_simplify'],
                    tag=token_tag,
                    synonyms=self.word2vec_model_service.get_synonyms(token_tag)
                )
            )
        return token_fields

    def _return_first_synonym(self, token_field: TokenFieldExtendedSchema):
        return token_field.synonyms[0][0].split("_")[0]

    def _adjust_word_case(self, model_token: Token, new_word: str):
        # Определяем падеж слова word2
        parsed_model_word = self.morph.parse(model_token.text)[0]
        case_model_word = parsed_model_word.tag.case

        # Преобразуем слово word1 в соответствии с падежом слова word2
        try:
            parsed_new_word = self.morph.parse(new_word)[0]
            inflected_new_word = parsed_new_word.inflect({case_model_word})
            if inflected_new_word:
                result = inflected_new_word.word
            else:
                result = model_token.text
            return result

        except:
            return new_word

    def _adjust_word_plurality(self, model_token: Token, new_word: str):
        parsed_model_word = self.morph.parse(model_token.text)[0]
        is_plural = True if parsed_model_word.tag.number == 'plur' else False
        is_singular = True if parsed_model_word.tag.number == 'sing'else False

        try:
            parsed_word = self.morph.parse(new_word)[0]
            if is_plural:
                result = parsed_word.make_agree_with_number(2).word
            if is_singular:
                result = parsed_word.make_agree_with_number(1).word  # приводим к единственному числу
            return result

        except:
            return new_word

    def _adjust_word_capitalization(self, model_token: Token, new_word: str):
        is_capitalize = model_token.is_title

        if is_capitalize:
            return new_word.title()
        return new_word

    def _create_simplified_text(self):
        simplified_text = []
        text_list = self._create_text_list(self.token_fields)
        for i, token in enumerate(self.token_list):
            if token.is_alpha:
                is_punc_next = self.token_list[i + 1].is_ascii
                if token.is_title:
                    if not text_list[i]:
                        print("Bla")
                    simplified_text.append(text_list[i] + " ")
                else:
                    if is_punc_next:
                        simplified_text.append(text_list[i])
                    else:
                        simplified_text.append(text_list[i] + " ")
            else:
                simplified_text.append(text_list[i] + " ")
        return "".join(simplified_text)

    def _create_text_list(self, token_fields: list[TokenFieldExtendedSchema]):
        text_list: list[str] = []
        for i, token_field in enumerate(token_fields):
            model_token = self.token_list[i]

            if not token_field.is_to_simplify:
                text_list.append(token_field.text)
                continue

            if not token_field.synonyms:
                text_list.append(token_field.text)
                continue

            processed_synonym = self._return_first_synonym(token_field)
            for function in self.synonym_pipeline:
                processed_synonym = function(model_token, processed_synonym)

            print(f"Word '{token_field.text}' was simplified into '{processed_synonym}'")
            text_list.append(processed_synonym)
        return text_list

    def return_simplification_model_data(self):
        return (
            SimplificationTextSchema(
                initial_text_id=self.assessment_model.initial_text_id,
                spacy_doc=self.assessment_model.spacy_doc,
                tokens=self.token_fields,
                initial_score=self.assessment_model.initial_score,
                simplified_text=self._create_simplified_text()
            )
        )



