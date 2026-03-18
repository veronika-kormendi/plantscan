import Levenshtein
import os
import string

input1 = "mommy"
input2 = "mommy"

dist_calc = Levenshtein.distance(input1, input2)
l_ratio = Levenshtein.ratio(input1, input2)

print(f"The Levenshtein distance between {input1} and {input2} is : {dist_calc}")
print(f"the Levenshtein similarity ratio is : {l_ratio}")

my_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\output"
def count_words(folder):
    total_words = 0
    # txt_files = [file for file in os.listdir(folder) if file.endswith(".txt")]
    for file in os.listdir(folder):
        if not file.endswith(".txt"): continue
        with open(os.path.join(folder, file)) as file:
            for line in file:
                # line = line.translate(str.maketrans("", "", string.punctuation))
                line = line.strip()
                words = line.split()
                total_words += len(words)
    print(f"There are {total_words} words in total.")
    return total_words
count_words(my_folder) #counting all the words in all the files
