import os
import sys
from pathlib import Path

import gensim
import wget
from spacy.lang.ru import Russian
from ufal.udpipe import Model, Pipeline

from assessement.schemas import AssessmentTextSchema

nlp = Russian()
# filepath = Path(__file__).parent / "word2vec_model.bin"
filepath = Path(__file__).parent / "212.zip"
# word2vec_model = KeyedVectors.load_word2vec_format("word2vec_model.bin.gz", binary=True, limit=1000000)

sample_text = ("Как усыновить ребёнка. "
                "Пройдите бесплатную подготовку в школе приёмных родителей. В некоторых случаях проходить подготовку не нужно."
                "Пройдите бесплатное медицинское освидетельствование. Это нужно, чтобы убедиться в отсутствии у вас заболеваний, при которых усыновление запрещено."
                "Получите заключение органа опеки и попечительства о возможности быть усыновителем."
                "Подайте в орган опеки и попечительства по месту жительства заявление с просьбой выдать заключение и приложите к нему необходимые документы."
                "Выберите ребёнка для усыновления и познакомьтесь с ним."
                "Ребёнка можно выбрать из государственного банка данных детей, оставшихся без попечения родителей."
                "После выбора ребёнка получите направление на его посещение по месту фактического нахождения. В течение десяти рабочих дней посетите ребёнка, установите с ним контакт и сообщите о своём решении в орган опеки и попечительства."
                "Подайте документы в суд."
                "Заявление подаётся в районный суд по месту жительства ребёнка. Сведения, которые надо указать в заявлении, и необходимые документы представлены в статье двести семьдесят, двести семьдесят один Гражданского процессуального кодекса."
                "Госпошлина за подачу заявления не взимается."
                "Примите участие в рассмотрении дела в суде."
                "После заседания вам выдадут решение об усыновлении ребёнка. Документ вступает в силу через десять календарных дней после вынесения решения. По ходатайству усыновителя судья может указать в решении, что оно предназначено к немедленному исполнению, и выдать копию решения суда в конце заседания."
                "Заберите ребёнка домой."
                "После вступления решения суда в силу посетите ребёнка по месту его жительства и заберите домой. Возьмите с собой решение суда и паспорт."
                "Зарегистрируйте усыновление.")

# initial_text_model = InitialText(text=sample_text)
#
# # class SpacyService:
# #
# #     def __init__(self):
#
# # Build pipes
# nlp.add_pipe('sentencizer')
#
# # Tokenize text
# doc = nlp(sample_text)
#
# assessment_model = AssessmentTextSchema(initial_text=initial_text_model, spacy_doc=doc.to_bytes())
# # Calculate number of sentences
# # retrieved_doc = Doc(nlp.vocab).from_bytes(assessment_model.spacy_doc)
# # retrieved_doc_02 = assessment_model.retrieve_doc()
#
# sentences = len([sent.text for sent in doc.sents])
#
# # Calculate number of words
# words = len([token for token in doc if token.is_alpha])

# Calculate number of syllables
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


def get_syllable_count():
    syllable_count = 0
    for token in doc:
        syllable_count += count_syllables(token.text)
    return syllable_count


def create_syllable_count_dict(tokenized_text=doc):
    return {token.text: count_syllables(token.text) for token in tokenized_text if token.is_alpha}


def filter_out_simple_words(text_dictionary: dict):
    return [word for word, value in text_dictionary.items() if value > 4]
    # words = []
    # for word, value in text_dictionary.items():
    #     if value > 4:
    #         words.append(word)
    # return words


# syllables = get_syllable_count()
#
# # Calculate ASL (average sentence length)
# ASL = words/sentences
#
# # Calculate ASW (average number of syllables per word)
# ASW = syllables/words
#
# # Calculate complexity index
# FRE = 206.835 - 1.52 * ASL - 65.14 * ASW


# Tokenize text
# Vectorize text


# word_to_simplify_dict = create_syllable_count_dict()
# words_to_simplify_list = filter_out_simple_words(word_to_simplify_dict)


# def find_synonyms(target_word, topn=5):
#     synonyms = []
#
#     if target_word in word2vec_model:
#         most_similar_words = word2vec_model.most_similar(target_word, topn=topn)
#
#         for word, score in most_similar_words:
#             synonyms.append(word)
#
#     return synonyms
#
# input_word = "business"
# synonyms = find_synonyms(input_word)


# model_url = 'http://vectors.nlpl.eu/repository/20/212.zip'
# m = wget.download(model_url)
# model_file = model_url.split('/')[-1]
# with zipfile.ZipFile(filepath, 'r') as archive:
#     stream = archive.open('model.bin')
    # model = KeyedVectors.load_word2vec_format(stream, binary=True)
# wn = RuWordNet()
# for sense in wn.get_senses('государственного'):
#     print(sense.synset)

# synonyms = wn.get_senses('государственного')[0].synset.hypernyms[0]
# hand_tool = wn1.synsets('государственный')
def process(pipeline, text=sample_text, keep_pos=True, keep_punct=False):
    entities = {'PROPN'}
    named = False
    memory = []
    mem_case = None
    mem_number = None
    tagged_propn = []

    # обрабатываем текст, получаем результат в формате conllu:
    processed = pipeline.process(text)

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
                    lemma = num_replace(token)
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


def num_replace():
    pass


def tag_ud(words: list[str], modelfile='udpipe_syntagrus.model'):
    udpipe_model_url = 'https://rusvectores.org/static/models/udpipe_syntagrus.model'
    udpipe_filename = udpipe_model_url.split('/')[-1]
    filepath = r'C:\Users\Евгения\PycharmProjects\models\udpipe_syntagrus.model'
    if not os.path.isfile(filepath):
        print('UDPipe model not found. Downloading...', file=sys.stderr)
        wget.download(udpipe_model_url)

    print('\nLoading the model...', file=sys.stderr)
    model = Model.load(filepath)
    process_pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

    print('Processing input...', file=sys.stderr)
    tagged = []
    for word in words:
        # line = unify_sym(line.strip()) # здесь могла бы быть ваша функция очистки текста
        output = process(process_pipeline, text=word)
        tagged_line = ' '.join(output)
        tagged.append(tagged_line)
    return tagged


preprocessed_text = tag_ud(words=words_to_simplify_list)
# print(preprocessed_text[:350])


# model_url = 'http://vectors.nlpl.eu/repository/20/180.zip'
# m = wget.download(model_url)
# model_file = model_url.split('/')[-1]

# nlpl_zip = "C:/Users/Евгения/PycharmProjects/accessibility_v2/180.zip"
# with zipfile.ZipFile(nlpl_zip, 'r') as archive:
#     # stream = archive.open('model.bin')
#     # model = gensim.models.KeyedVectors.load_word2vec_format(stream, binary=True)
#     archive.extract('model.bin')  # Извлечение файла model.bin из архива
#     model = gensim.models.KeyedVectors.load_word2vec_format('model.bin', binary=True)

nlpl_model = gensim.models.KeyedVectors.load_word2vec_format('model.bin', binary=True)


def process_synonyms():
    for word in preprocessed_text:
        # есть ли слово в модели? Может быть, и нет
        if word in nlpl_model:
            print(word)
            print_most_similar(word)
        else:
            # Увы!
            print(word + ' is not present in the model')


def print_most_similar(preprocessed_word: str):
    # выдаем 10 ближайших соседей слова:
    for i in nlpl_model.most_similar(positive=[preprocessed_word], topn=10):
        # слово + коэффициент косинусной близости
        print(f"Synonym found using most_similar() {i[0]}, {i[1]}")
        print_synonyms_relative_cosine_similarity(preprocessed_word, i[0])
    print('\n')


def print_synonyms_relative_cosine_similarity(preprocessed_word: str, synonym):
    topn = 5  # Number of closest synonyms to retrieve
    similarity_index = nlpl_model.relative_cosine_similarity(wa=preprocessed_word, wb=synonym, topn=topn)
    print(f"Similarity index for {synonym}: {similarity_index}")


process_synonyms()

print(doc)