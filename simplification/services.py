import os
import sys
import zipfile

import gensim
import wget
from ufal.udpipe import Model, Pipeline

from assessement.models import AssessmentTextModel
from assessement.utils import count_syllables
from simplification.schemas import SimplificationTextSchema, TokenFieldExtendedSchema


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
                self.print_most_similar(word)
            else:
                # Увы!
                print(word + ' is not present in the model')

    def filter_by_pos(self, token_tag: str, synonym: str):
        token_pos = token_tag.split("_")[-1]
        synonym_pos = synonym.split("_")[-1]
        return True if token_pos == synonym_pos else False

    def print_most_similar(self, token_tags: list):
        if not token_tags:
            return []

        for token_tag in token_tags:
            if token_tag not in self.model:
                return []
        # выдаем 10 ближайших соседей слова:
        synonyms: list[tuple] = []

        for i in self.model.most_similar(positive=[token_tags[0]], topn=10):
            antonyms = self.model.most_similar(negative=[token_tags[0]], topn=10)
            # слово + коэффициент косинусной близости
            print(f"Synonym found using most_similar() {i[0]}, {i[1]}")
            is_antonym = True if i[0] in antonyms else False
            # TODO: Filter our synonyms
            # Filter out by complexity
            is_lower_complexity = True if count_syllables(i[0]) < 4 else False
            # Filter our by part of speach
            is_same_pos = self.filter_by_pos(token_tags[0], i[0])
            # Filter out by closeness
            is_close = True if i[1] > 0.6 else False
            if is_same_pos and is_lower_complexity and is_close and not is_antonym:
                synonyms.append((i[0], i[1]))
            # self.print_synonyms_relative_cosine_similarity(preprocessed_word, i[0])
        return synonyms
        print('\n')

    def print_synonyms_relative_cosine_similarity(self, preprocessed_word: str, synonym):
        topn = 5  # Number of closest synonyms to retrieve
        similarity_index = self.model.relative_cosine_similarity(wa=preprocessed_word, wb=synonym, topn=topn)
        print(f"Similarity index for {synonym}: {similarity_index}")


class SimplificationService:

    def __init__(self, assessment_model: AssessmentTextModel):
        self.assessment_model = assessment_model
        self.udpipe_model_service = UdPipeModelService()
        self.word2vec_model_service = VectorModelService()

    def _create_tokens_field(self):
        token_fields: list[TokenFieldExtendedSchema] = []
        for token_field in self.assessment_model.tokens:
            token_text = token_field['text']
            token_tag = self.udpipe_model_service.process(token_field['text'])
            token_fields.append(
                TokenFieldExtendedSchema(
                    text=token_text,
                    syllables_count=token_field['syllables_count'],
                    is_to_simplify=token_field['is_to_simplify'],
                    tag=token_tag,
                    synonyms=self.word2vec_model_service.print_most_similar(token_tag)
                )
            )
        return token_fields

    def _create_simplified_text(self, token_fields: list[TokenFieldExtendedSchema]):
        text_list: list[str] = []
        for token in token_fields:
            if not token.is_to_simplify:
                text_list.append(token.text)
                continue

            if not token.synonyms:
                text_list.append(token.text)
                continue

            synonym = token.synonyms[0][0].split("_")[0]
            text_list.append(synonym)
        return " ".join(text_list)

    def return_simplification_model_data(self):
        token_fields = self._create_tokens_field()
        return (
            SimplificationTextSchema(
                initial_text_id=self.assessment_model.initial_text_id,
                spacy_doc=self.assessment_model.spacy_doc,
                tokens=token_fields,
                initial_score=self.assessment_model.initial_score,
                simplified_text=self._create_simplified_text(token_fields)
            )
        )



