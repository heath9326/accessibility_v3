import statistics
import time
from assessement.models import InitialText, AssessmentTextModel
from assessement.schemas import InitialTextSchema
from assessement.services import ComplexityAssessmentService
from googletrans import Translator

all_number_of_words = []
all_number_of_sentences = []
all_number_of_syllables = []
all_complexity_scores = []

all_final_number_of_words = []
all_final_number_of_sentences = []
all_final_number_of_syllables = []
all_final_complexity_scores = []

def load_texts():
    with open('dataset.txt', mode='r') as file:
        texts = []
        all_texts = file.read().split('\n\n')  # Split by empty lines

        for text_block in all_texts:
            texts.append(text_block)#
        return texts

texts = load_texts()

def translate_text(text, dest_lang='en'):
    translator = Translator()
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

# Translate text from Russian to English
russian_text = "Привет, как дела?"
english_translation = translate_text(russian_text, dest_lang='en')
print("Russian Text:", russian_text)
print("English Translation:", english_translation)

# Translate text from English back to Russian
english_text = "Hello, how are you?"
russian_translation = translate_text(english_text, dest_lang='ru')
print("English Text:", english_text)
print("Russian Translation:", russian_translation)


for i, sample_text in enumerate(texts):
    print("\n")
    print(f"Original Text: \n {sample_text}")
    rus_to_eng_text = translate_text(sample_text, dest_lang='en')
    time.sleep(5)
    eng_to_rus_text = translate_text(rus_to_eng_text, dest_lang='ru')
    print(f"Result Text: \n {eng_to_rus_text}")

    print("\n")

    print(f"Processing sample text № {i}.")
    initial_text_data = InitialTextSchema(text=eng_to_rus_text)
    initial_text_model = InitialText(**initial_text_data.model_dump())
    # TODO: in API create this model in DB

    initial_assessment_service = ComplexityAssessmentService(initial_text_model)
    complexity_assessment_data = initial_assessment_service.return_assessment_model_data()

    number_of_words = initial_assessment_service.calculate_words()
    all_number_of_words.append(number_of_words)
    print(f"Number of words: {number_of_words}")

    number_of_sentences = initial_assessment_service.calculate_sentences()
    all_number_of_sentences.append(number_of_sentences)
    print(f"Number of sentences: {number_of_sentences}")

    number_of_syllables = initial_assessment_service.calculate_syllables()
    all_number_of_syllables.append(number_of_syllables)
    print(f"Number of syllables: {number_of_syllables}")

    complexity = initial_assessment_service.calculate_complexity()
    all_complexity_scores.append(complexity)
    print(f"Initial Complexity score: {complexity}")

    complexity_assessment_model = AssessmentTextModel(**complexity_assessment_data.model_dump())
print("\n")

print("\n")
print(f"all_number_of_words: {all_number_of_words}")
print(f"Average number of all_number_of_words: {statistics.mean(all_number_of_words)}")
print(f"Median number of all_number_of_words: {statistics.median(all_number_of_words)}")
print(f"Min number of all_number_of_words: {min(all_number_of_words)}")
print(f"Max number of all_number_of_words: {max(all_number_of_words)}")
print("\n")

print("\n")
print(f"all_number_of_sentences: {all_number_of_sentences}")
print(f"Average number of all_number_of_sentences: {statistics.mean(all_number_of_sentences)}")
print(f"Median number of all_number_of_sentences: {statistics.median(all_number_of_sentences)}")
print(f"Min number of all_number_of_sentences: {min(all_number_of_sentences)}")
print(f"Max number of all_number_of_sentences: {max(all_number_of_sentences)}")
print("\n")

print("\n")
print(f"all_number_of_syllables: {all_number_of_syllables}")
print(f"Average number of all_number_of_syllables: {statistics.mean(all_number_of_syllables)}")
print(f"Median number of all_number_of_syllables: {statistics.median(all_number_of_syllables)}")
print(f"Min number of all_number_of_syllables: {min(all_number_of_syllables)}")
print(f"Max number of all_number_of_syllables: {max(all_number_of_syllables)}")
print("\n")

print("\n")
print(f"all_complexity_scores: {all_complexity_scores}")
print(f"Average number of all_complexity_scores: {statistics.mean(all_complexity_scores)}")
print(f"Median number of all_complexity_scores: {statistics.median(all_complexity_scores)}")
print(f"Min number of all_complexity_scores: {min(all_complexity_scores)}")
print(f"Max number of all_complexity_scores: {max(all_complexity_scores)}")
print("\n")
