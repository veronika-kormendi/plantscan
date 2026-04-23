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

def perform_ocr_on_single_image(cropped_img_path, ocr_output_folder_path="ocr_txt_folder"):
    """Perform OCR on a single image
    :param cropped_img_path: path to cropped image
    :param ocr_output_folder_path:
    :return: extracted text from cropped image"""
    os.makedirs(ocr_output_folder_path, exist_ok=True) # create output folder
    ocr = PaddleOCR(use_doc_orientation_classify=True,  # create ocr object
                    use_doc_unwarping=False,
                    use_textline_orientation=False, )
    print(f"Performing OCR on {cropped_img_path}")
    result = ocr.predict(cropped_img_path) # extract text
    base = os.path.splitext(os.path.basename(cropped_img_path))[0] # e.g. IMG_8590_cropped
    json_path = os.path.join(ocr_output_folder_path, f"{base}.json") # for json e.g. IMG_8590_cropped_res.json
    txt_path = os.path.join(ocr_output_folder_path, f"{base}.txt")
    for res in result:
        res.print()
        res.save_to_json(json_path) # save json to the output folder
        res.save_to_img(ocr_output_folder_path) # save img to output folder
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    text_lines = data.get("rec_texts", [])
    with open(txt_path, "w", encoding="utf-8") as f:
        for line in text_lines:
            f.write(line + "\n")
    print(f"finished OCR on {cropped_img_path}.")
    # print(f"txt path: {txt_path}.") # displayed for debugging
    return txt_path