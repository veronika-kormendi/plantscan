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
    totals_per_txt_files = {} # to store the word counts per file
    grand_total = 0
    for file in os.listdir(folder): # go through each txt file in the output folder
        if not file.endswith(".txt"): continue
        file_path = os.path.join(folder, file)
        word_count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                translator = str.maketrans(string.punctuation, " " * len(string.punctuation)) # replace punct with space
                line = line.translate(translator) # apply spaces
                words = line.split()
                word_count += len(words)
                # print(line)
        print(f"There are {word_count} words in the file {file}")
        totals_per_txt_files[file] = word_count
        grand_total += word_count

    return totals_per_txt_files, grand_total
count_words(my_folder) #counting all the words in all the files
print("\n")
annot_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\annotation"
count_words(annot_folder)