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
from config import (JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER, CLEANED_FOLDER_PATH, ANNOTATION_FOLDER, DEFAULT_RESIZE_WIDTH,
                    SUPPORTED_IMAGE_TYPES,
                    OCR_SETTINGS, CROPPED_FOLDER, )

# step 1 - img conversion: HEIC to JPG
def heic_to_jpg(input_image_folder_path, output_folder_path):
    """convert heic to jpg extension
    :param input_image_folder_path: input image's path
    :param: output_folder_path: path where to save the jpg image
    :return: jpg image path"""
    pillow_heif.register_heif_opener() # to be able to open HEIC files
    if not os.path.exists(output_folder_path): # if folder does not exist
        os.makedirs(output_folder_path, exist_ok=True) # create folder
    filename = os.path.basename(input_image_folder_path) # getting the filename
    # remove HEIC extension and replace it with jpg
    jpg_filename = f"{os.path.splitext(filename)[0]}.jpg" # "IMG_7474", ".HEIC" --> IMG_7476.jpg
    jpg_path = os.path.join(output_folder_path, jpg_filename) #build the jpg path where to save the jpg img
    try:
        img = Image.open(input_image_folder_path) # open from input path
        img.save(jpg_path, format='JPEG') #save jpg
    except Exception as error: # error handling
        print(f"HEIC conversion error occured: {error}") # display error message
        return
    print(f"HEIC conversion from {filename} to jpg {jpg_filename}") # display output
    return jpg_path

def colour_to_greyscale(input_folder, coloured_img, output_path):
    """turn coloured image into greyscale image
    :param input_folder: input image's folder path
    :param coloured_img: coloured image
    :param output_folder_path: the folder where the greyscale image is saved
    :return: the filepath of the greyscale image"""
    # path = join input folder & selected coloured image
    input_img_path = os.path.join(input_folder, coloured_img) # image to greyscale
    if not os.path.exists(output_path): # if folder does not exist
        os.makedirs(output_path, exist_ok=True) # make folder & don't throw error if already exist
    gscale_output_filepath = os.path.join(output_path, coloured_img) # build path where to save the gscale img
    gscale_filename = os.path.basename(gscale_output_filepath) # get the gscale filename
    coloured_img = cv.imread(input_img_path) # read image
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY) # turn it to greyscale
    cv.imwrite(gscale_output_filepath, greyscale_img) # save gscale img to the gscale output folder
    print(f"Greyscale conversion successful: {gscale_filename} is greyscale now.")
    return gscale_output_filepath

def select_img_from():
    """Select an image from the input folder to start the pipeline.
    :returns: filepath of the image to be opened i.e. selected file"""
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=SUPPORTED_IMAGE_TYPES)
    if not file_to_open:
        return None
    return file_to_open

def resize_image(image, new_w=DEFAULT_RESIZE_WIDTH):
    """Resize an image to a new width and height.
    :param image: image to be resized
    :param new_w: new width
    :returns: resized image"""
    img_w, img_h = image.size # img width and height
    new_h = int(img_h * new_w / img_w)
    resized_image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return resized_image

def make_tk_img(resized_image):
    """turn image opened with PIL to tk compatible image
    :param resized_image: resized image
    :returns: tk_img: tk image"""
    tk_img = ImageTk.PhotoImage(resized_image)
    return tk_img

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
    print(f"finished performing OCR on {cropped_img_path}.")
    # print(f"txt path: {txt_path}.") # displayed for debugging
    return txt_path

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

# def save_crop_and_start_ocr():
#     #1. save cropped image
#     cropped_img_path = save_cropped_img()
#     print(f"Saved cropped image to {cropped_img_path}.")
#     if cropped_img_path is None:
#         return
#     #2. extract text
#     # ocr_extracted = perform_ocr_on_single_image(cropped_folder) #folderpath was passed in
#     ocr_extracted = perform_ocr_on_single_image(cropped_img_path)
#     if ocr_extracted is not None:
#         print(f"ocr performed on: {ocr_extracted}") #display the current text file
#         display_extracted = load_words(ocr_extracted) # display the extracted text before cleaning
#         print(f"OCR extracted text before cleaning: {display_extracted}")
#         cleaned_extracted_text = count_word_and_char(ocr_extracted, file_type="ocr") # clean extracted text
#         display_cleaned_extracted_text = load_words(cleaned_extracted_text) #load cleaned extracted text
#         print(f"OCR extracted text after cleaning: {display_cleaned_extracted_text}") #display the cleaned extracted text
#         display_extracted_char_level = load_text(cleaned_extracted_text)  #load the text for character level accuracy
#         print(f"char level ocr text: {display_extracted_char_level}") # display cleaned extracted text for char level accuracy
#         print("\n")
#         # get_img_id(ocr_extracted) #test id function
#         # print(f"extracted image id {get_img_id(ocr_extracted)}") #test
#         # get_img_id(cropped_img_path) # test
#         # print(f"image id {get_img_id(cropped_img_path)}") #test
#         # go through annotation folder and check each file if it matches with the image id
#         #if there is a match,
#         #load that file and display
#         # clean text and count words, chars in that file
#         #display it after cleaning
#         gt_file_path = None
#         annotation_id = None
#         ocr_img_id = get_img_id(ocr_extracted)
#         print(f"OCR img id: {ocr_img_id}")
#         for root, dirs, files in os.walk(ANNOTATION_FOLDER): # go through root folder path, subfolders and files
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 annotation_id = get_img_id(file_path)
#                 if annotation_id == ocr_img_id:
#                     gt_file_path = file_path
#                     break
#                 if gt_file_path:
#                     break
#         display_gt_text = load_words(gt_file_path)
#         print(f"gt_text before cleaning: {display_gt_text}")
#         cleaned_gt_text = count_word_and_char(gt_file_path, file_type="gt")
#         display_cleaned_gt_text = load_words(cleaned_gt_text)
#         print(f"gt_text after cleaning: {display_cleaned_gt_text}")
#         display_gt_char_level = load_text(cleaned_gt_text)
#         print(f"char level text: {display_gt_char_level}")
#         char_level_edit_dist = Levenshtein.distance(display_gt_char_level,display_extracted_char_level)
#         # calculate Levensthein distance
#         word_level_edit_distance = Levenshtein.distance(display_cleaned_extracted_text,display_cleaned_gt_text) # word level accuracy
#         print(f"word level edit distance between extracted and gt {ocr_img_id, annotation_id}: {word_level_edit_distance}")
#         print(f"char level edit distance {char_level_edit_dist}")
#         print()
#         lev_ratio_word_level = Levenshtein.ratio(display_cleaned_extracted_text,display_cleaned_gt_text)
#         lev_ratio_char_level = Levenshtein.ratio(display_gt_char_level, display_extracted_char_level)
#         print(f"Levenshtein ratio: {lev_ratio_word_level}")
#         print(f"Levenshtein ratio: {lev_ratio_char_level}")

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
#not used atm //count_word_and_char() needs a filetype
# def load_and_clean_word(txt_input_file):
#     word_level_text_before_cleaning = load_words(txt_input_file) #load text for word level
#     cleaned_text = count_word_and_char(txt_input_file) #clean and count words
#     load_cleaned =load_words(cleaned_text)
#     print(f"text before cleaning: {word_level_text_before_cleaning}")
#     print(f"text after cleaning: {load_cleaned}")
#     # cleaned_text = " ".join(cleaned_text)
#     return cleaned_text


def find_matching_gt_file(ocr_file_path):
    ocr_img_id = get_img_id(ocr_file_path)
    for root, dirs, files in os.walk(ANNOTATION_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            annotation_id = get_img_id(file_path)
            if annotation_id == ocr_img_id: #if there is a match
                return file_path
    return None

def calculate_cer():
    pass


def calculate_wer_manual(word_edit_distance, gt_word_count):
    """
    Calculate Word Error Rate (WER) using edit distance and GT word count.
    :param word_edit_distance: Levenshtein distance between GT words and OCR words
    :param gt_word_count: number of words in the GT text
    :return: WER value (float)
    """
    if gt_word_count == 0:
        return 0.0  # no GT words → no errors possible

    wer_value = word_edit_distance / gt_word_count
    return wer_value


def calculate_error_rates():
    pass

# def calculate_wer(gt_text, extracted_text):
#     wer_value = wer(gt_text, extracted_text)
#     return wer_value
