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







def is_it_plant_based(input_file_path):
    """this function takes a txt file and checks
    if any words from the exclude list matches with the currently examined word
    if there is a match: False -not plant based
    if there is a match: True - plant based"""
    words_to_check = load_words(input_file_path)
    print(f"words_to_check: {words_to_check}")
    # for word in words_to_check:
