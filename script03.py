import pymorphy2
from natasha import MorphVocab, NamesExtractor

morph = pymorphy2.MorphAnalyzer()

word1 = 'инфекция'
word2 = 'заболеваниях'

parsed_word = morph.parse(word2)[0]  # получаем разбор слова
singular_form = parsed_word.make_agree_with_number(1).word  # приводим к единственному числу
singular_forms.append(singular_form)

print(singular_forms)