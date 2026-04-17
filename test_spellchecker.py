
from spellchecker import SpellChecker

spell = SpellChecker() # load default word frequency list

# find those words that may be misspelled
misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])
test2 =['ingredients', 'soya', 'beans', 'water', 'salt', 'firmingagent', 'calciumchloridemesm', 'chloride']
misspelled_test2 = spell.unknown(test2)
for word in misspelled:
    print(f"misspelt: {misspelled}")
    # Get the one `most likely` answer
    print(f"correction: {spell.correction(word)}")

    # Get a list of `likely` options
    print(spell.candidates(word))

# for word in misspelled_test2:
#     print(f"candidates: {spell.candidates(word)}")
#     print(f" correction: {spell.correction(word)}")
#
#
# print(f"unknown words: {spell.unknown(misspelled_test2)}")
# print(f" number of misspelled words: {len(misspelled_test2)}")
# print(type(spell.word_frequency))
# spell.word_frequency.load_text_file('./added_words.txt')