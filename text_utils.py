
import os # for file handling
from PIL import Image, ImageTk  # for managing images
import pillow_heif # for HEIC to JPG conversion
import cv2 as cv # openCV
from tkinter import filedialog
from jiwer import wer
from paddleocr import PaddleOCR
import json
import string
import unicodedata
import Levenshtein
# # for testing coloured images with gui2
# from config import (JPG_OUTPUT_FOLDER, CLEANED_FOLDER_PATH, ANNOTATION_FOLDER, DEFAULT_RESIZE_WIDTH,
#                     SUPPORTED_IMAGE_TYPES,
#                     OCR_SETTINGS, CROPPED_FOLDER, )

from config import (JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER, CLEANED_FOLDER_PATH, ANNOTATION_FOLDER, DEFAULT_RESIZE_WIDTH,
                    SUPPORTED_IMAGE_TYPES,
                    OCR_SETTINGS, CROPPED_FOLDER )
import csv
from spellchecker import SpellChecker # for postprocessing
import pandas as pd
spell = SpellChecker() # load default word frequency list
extra_words = ["flavouring", "sucralose", "colours", "sorbate", "sugar", "caramelised", "flavour", "guar", "thermophilus",
               "bulgaricus", "lecithins", "folic", "fibre", "sucralose", "stabiliser", "stabilisers", "curcumin",
               "xanthan", "sundried", "crouton", "croutons", "colour", "humectants", "acerola", "pasteurised", "coagulans", "flavourings"]
# add extra words to spell checker dictionary
for word in extra_words:
    spell.word_frequency.add(word)

# function to clean a line of text
def clean_line(line):
    line = line.strip() # remove whitespaces (tab, space, new line)
    line = line.lower() # make it lowercase
    line = unicodedata.normalize("NFKC", line)  # remove unicode chars
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))  # replace punct with space
    line = line.translate(translator)  # apply spaces
    #remove numbers
    empty_string = ""
    for char in line: # go through every character in line
        if not char.isdigit(): # check if the char is not digit
            empty_string += char # if not digit, add it to the empty string
    line = empty_string # empty string becomes the cleaned line (free from numbers, special characters)
    return line # return the cleaned line
#remove extra white spaces
def normalize_for_char_metric(text: str) -> str:
    #split on any white spaces, then join them
    return " ".join(text.split())

def count_word_and_char(text_file, file_type="ocr"):
    """
    Cleans the text, counts the number of words and chars in a text file.
    :param text_file: input file path
    :param file_type: type of file either ocr or gt
    :return: cleaned text path
    """
    word_count = 0
    char_count = 0
    cleaned_lines =[]
    if not os.path.exists(CLEANED_FOLDER_PATH):
        os.makedirs(CLEANED_FOLDER_PATH)
    origin = os.path.basename(text_file)
    without_extension = os.path.splitext(origin)[0]
    # cleaned_filename = f"{without_extension}_cleaned_super.txt"
    if file_type == "gt":
        cleaned_filename = f"{without_extension}_cleaned_gt.txt"
    else:
        cleaned_filename = f"{without_extension}_cleaned_ocr.txt"
    cleaned_path = os.path.join(CLEANED_FOLDER_PATH, cleaned_filename)
    with open(text_file, "r", encoding="utf-8") as f:
        for line in f:
            cleaned_line = clean_line(line)
            cleaned_lines.append(cleaned_line)
            words = cleaned_line.split()
            word_count += len(words)
            for word in words:
                char_count += len(word)
            # print(cleaned_line)
    with open(cleaned_path, "w", encoding="utf-8") as out:
        out.write("\n".join(cleaned_lines))
    print(f"cleaned text was saved to {cleaned_path}.")
    print(f"There are {word_count} words and {char_count} chars in this file: '{text_file}'\n")
    return cleaned_path

def load_words(txt_input_file): # use this for word-level comparison
    """Loads a text file and return a list of words.
    :parameter txt_input_file: Path to the text file.
    :return: List of words."""
    with open(txt_input_file, "r", encoding="utf-8") as f:
        return f.read().split() #return  text as list of words

def load_text(txt_input_file): # use this for char-level comparison
    with open(txt_input_file, "r", encoding="utf-8") as f:
        return f.read() # return the entire text as a string

def load_and_clean_char(txt_input_file):
    word_level_text_before_cleaning = load_text(txt_input_file) #load text for word level
    cleaned_text = count_word_and_char(txt_input_file) #clean and count words
    load_cleaned =load_text(cleaned_text)
    print(f"text before cleaning: {word_level_text_before_cleaning}")
    print(f"text after cleaning: {load_cleaned}")
    return cleaned_text

def get_img_id(path):
    """extract image id from file path
    :param path: file path
    :return: image id
    """
    filename = os.path.basename(path)
    img_id = os.path.splitext(filename)[0]
    parts = img_id.split("_") # split to parts by _
    if len(parts) >=2 and parts[0].upper() == "IMG":
        return f"{parts[0]}_{parts[1]}"
    return img_id

def each_word_on_new_line(input_folder_path, output_folder_path):
    os.makedirs(output_folder_path, exist_ok=True) # create output folder
    for filename in os.listdir(input_folder_path):
        in_path = os.path.join(input_folder_path, filename)
        with open(in_path, "r", encoding="utf-8") as f:
            text = f.read()
        words = text.split()
        cleaned = [w.strip() for w in words if w.strip()]
        out_path = os.path.join(output_folder_path, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            for word in cleaned:
                f.write(word + "\n")

    return output_folder_path