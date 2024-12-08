
def count_syllables(word: str) -> int:
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


def load_texts():
    with open('dataset.txt', mode='r') as file:
        texts = []
        all_texts = file.read().split('\n\n')  # Split by empty lines

        for text_block in all_texts:
            texts.append(text_block)#
        return texts