import os, unicodedata, string
import Levenshtein

my_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\output"
annot_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\annotation"

def clean_line(line):
    line = line.strip()
    line = unicodedata.normalize("NFKC", line)  # remove unicode chars
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))  # replace punct with space
    line = line.translate(translator)  # apply spaces
    #remove numbers
    empty_string = ""
    for char in line:
        if not char.isdigit():
            empty_string += char
    line = empty_string
    return line

def count_w(folder):
    totals_per_txt_files = {}  # to store the word counts per file
    total_words = 0
    total_chars = 0
    for file in os.listdir(folder):  # go through each txt file in the output folder
        if not file.endswith(".txt"): continue
        file_path = os.path.join(folder, file)
        word_count = 0
        char_count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                cleaned_line = clean_line(line)
                words = cleaned_line.split()
                word_count += len(words) # count the num of words
                for word in words:
                    char_count += len(word) # count chars
                print(cleaned_line)
        print(f"There are {word_count} words and {char_count} chars in the file {file}\n")
        totals_per_txt_files[file] = {
            "words": word_count,
            "chars": char_count
        }
        total_words += word_count #sum them all
        total_chars += char_count
    return totals_per_txt_files, total_words, total_chars
count_w(my_folder)
count_w(annot_folder)


