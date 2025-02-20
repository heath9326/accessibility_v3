import statistics

from models.assessment import InitialText, AssessmentTextModel
from schemas.assessment import InitialTextSchema
from services.assessment import ComplexityAssessmentService
from models.simplification import SimplificationModel
from services.simplification import SimplificationService

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
for i, sample_text in enumerate(texts):
    print("\n")
    print(f"Processing sample text № {i}.")
    initial_text_data = InitialTextSchema(text=sample_text)
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
    # TODO: in API create this model in DB

    simplification_service = SimplificationService(complexity_assessment_model)
    simplification_model_data = simplification_service.return_simplification_model_data()
    simplification_model = SimplificationModel(**simplification_model_data.model_dump())
    print("\n")
    print(f"Simplified text of sample text # {i}:\n"
          f"{simplification_model.simplified_text}")
    # TODO: in API create this model in DB

    final_assessment_service = ComplexityAssessmentService(simplification_model)
    number_of_words = final_assessment_service.calculate_words()
    all_final_number_of_words.append(number_of_words)
    print(f"Final Number of words: {number_of_words}")

    number_of_sentences = final_assessment_service.calculate_sentences()
    all_final_number_of_sentences.append(number_of_sentences)
    print(f"Final Number of sentences: {number_of_sentences}")

    number_of_syllables = final_assessment_service.calculate_syllables()
    all_final_number_of_syllables.append(number_of_syllables)
    print(f"Final Number of syllables: {number_of_syllables}")

    final_complexity_score = final_assessment_service.calculate_complexity()
    all_final_complexity_scores.append(final_complexity_score)
    print("\n")
    print(f"Final Final complexity score of sample text № {i}: {final_complexity_score}")
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

"""Final calculations after simplification"""

print("\n")
print(f"all_final_number_of_words: {all_final_number_of_words}")
print(f"Average number of all_final_number_of_words: {statistics.mean(all_final_number_of_words)}")
print(f"Median number of all_final_number_of_words: {statistics.median(all_final_number_of_words)}")
print(f"Min number of all_final_number_of_words: {min(all_final_number_of_words)}")
print(f"Max number of all_final_number_of_words: {max(all_final_number_of_words)}")
print("\n")

print("\n")
print(f"all_final_number_of_sentences: {all_final_number_of_sentences}")
print(f"Average number of all_final_number_of_sentences: {statistics.mean(all_final_number_of_sentences)}")
print(f"Median number of all_final_number_of_sentences: {statistics.median(all_final_number_of_sentences)}")
print(f"Min number of all_final_number_of_sentences: {min(all_final_number_of_sentences)}")
print(f"Max number of all_final_number_of_sentences: {max(all_final_number_of_sentences)}")
print("\n")

print("\n")
print(f"all_final_number_of_syllables: {all_final_number_of_syllables}")
print(f"Average number of all_final_number_of_syllables: {statistics.mean(all_final_number_of_syllables)}")
print(f"Median number of all_final_number_of_syllables: {statistics.median(all_final_number_of_syllables)}")
print(f"Min number of all_final_number_of_syllables: {min(all_final_number_of_syllables)}")
print(f"Max number of all_final_number_of_syllables: {max(all_final_number_of_syllables)}")
print("\n")

print("\n")
print(f"all_final_complexity_scores: {all_final_complexity_scores}")
print(f"Average number of all_complexity_scores: {statistics.mean(all_final_complexity_scores)}")
print(f"Median number of all_complexity_scores: {statistics.median(all_final_complexity_scores)}")
print(f"Min number of all_complexity_scores: {min(all_final_complexity_scores)}")
print(f"Max number of all_complexity_scores: {max(all_final_complexity_scores)}")
print("\n")
