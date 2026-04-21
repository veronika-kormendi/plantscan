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
    print(f"finished OCR on {cropped_img_path}.")
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

def find_matching_gt_file(ocr_file_path):
    ocr_img_id = get_img_id(ocr_file_path)
    for root, dirs, files in os.walk(ANNOTATION_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            annotation_id = get_img_id(file_path)
            if annotation_id == ocr_img_id: #if there is a match
                return file_path
    return None


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

def calculate_cer_manual(char_edit_dist_norm, gt_norm):
    n = len(gt_norm) #total number of characters
    if n == 0:
        return 0.0
    cer_value = char_edit_dist_norm / n
    return cer_value

def calculate_cac(cer_value):
    #calculate character accuracy
    cac = 1 - cer_value
    return cac

def calculate_wac(wer_value):
    wac = 1 - wer_value
    return wac

# def calculate_wer(gt_text, extracted_text): #checking if wer calculation is correct by using jiwer.wer
#     wer_value = wer(gt_text, extracted_text)
#     return wer_value

# ###############################################################################################
# def evaluate_folder(folder_path, output_csv="ocr_metrics.csv"):
#     """function to produce metrics of OCR extraction
#     :param folder_path: folder contents are being evaluated (extracted text vs gt text)
#     :param output_csv: metric results saved to a csv file"""
#     results = [] # init results list
#     for filename in os.listdir(folder_path): # go through files in the folder
#         if not filename.endswith("_cleaned_ocr.txt"): # find ocr extracted file
#             continue
#         ocr_path = os.path.join(folder_path, filename) # get extracted text's filepath
#         img_id = get_img_id(filename) # extract image ID
#         gt_path = find_matching_gt_file(ocr_path) # find matching gt file for extracted text file based on the img ID
#         if not gt_path:
#             print(f"No GT found for {filename}")
#             continue
#         gt_cleaned = count_word_and_char(gt_path, file_type="gt") # get word, char count
#
#         # Load OCR cleaned text
#         ocr_text = load_text(ocr_path)
#         ocr_norm = normalize_for_char_metric(ocr_text)
#         ocr_words = load_words(ocr_path)
#
#         # Load GT cleaned text
#         gt_text = load_text(gt_cleaned)
#         gt_norm = normalize_for_char_metric(gt_text)
#         gt_words = load_words(gt_cleaned)
#
#         # Character-level metrics
#         char_edit = Levenshtein.distance(gt_text, ocr_text)
#         char_edit_norm = Levenshtein.distance(gt_norm, ocr_norm)
#         char_ratio = Levenshtein.ratio(gt_text, ocr_text)
#         char_ratio_norm = Levenshtein.ratio(gt_norm, ocr_norm)
#
#         cer = char_edit_norm / len(gt_norm) if len(gt_norm) > 0 else 0.0
#         cac = 1 - cer
#
#         # Word-level metrics
#         word_edit = Levenshtein.distance(gt_words, ocr_words)
#         word_ratio = Levenshtein.ratio(gt_words, ocr_words)
#
#         wer = word_edit / len(gt_words) if len(gt_words) > 0 else 0.0
#         wac = 1 - wer
#
#         results.append({
#             "image": img_id,
#             "char_edit": char_edit,
#             "char_edit_norm": char_edit_norm,
#             "char_ratio": char_ratio,
#             "char_ratio_norm": char_ratio_norm,
#             "cer": cer,
#             "cac": cac,
#             "word_edit": word_edit,
#             "word_ratio": word_ratio,
#             "wer": wer,
#             "wac": wac,
#         })
#
#     # Save CSV
#     if results:
#         keys = results[0].keys()
#         with open(output_csv, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=keys)
#             writer.writeheader()
#             writer.writerows(results)
#
#     print(f"Metrics saved to {output_csv}")
#     return results


def evaluate_preprocessed(folder_path, output_csv="preprocessed_metrics.csv"):
    results = []
    # Loop through cleaned OCR files
    for filename in os.listdir(folder_path):
        if not filename.endswith("_cleaned_ocr.txt"):
            continue

        ocr_path = os.path.join(folder_path, filename)

        # Derive base id, e.g. IMG_9163 from IMG_9163_cropped_cleaned_ocr.txt
        img_id = get_img_id(filename)

        # Find matching cleaned GT file in the same folder
        # e.g. IMG_9163_annotation_cleaned_gt.txt
        gt_path = None
        for f in os.listdir(folder_path):
            if f.endswith("_cleaned_gt.txt") and get_img_id(f) == img_id:
                gt_path = os.path.join(folder_path, f)
                break

        if not gt_path:
            print(f"No cleaned GT found for {filename}")
            continue

        # --- Load OCR cleaned text ---
        ocr_text = load_text(ocr_path)
        ocr_norm = normalize_for_char_metric(ocr_text)
        ocr_words = load_words(ocr_path)

        # --- Load GT cleaned text ---
        gt_text = load_text(gt_path)
        gt_norm = normalize_for_char_metric(gt_text)
        gt_words = load_words(gt_path)

        # --- Character-level metrics
        # ---
        char_edit = Levenshtein.distance(gt_text, ocr_text)
        char_edit_norm = Levenshtein.distance(gt_norm, ocr_norm)
        char_ratio = Levenshtein.ratio(gt_text, ocr_text)
        char_ratio_norm = Levenshtein.ratio(gt_norm, ocr_norm)

        cer = calculate_cer_manual(char_edit_norm, gt_norm)
        cac = calculate_cac(cer)

        # --- Word-level metrics ---
        word_edit = Levenshtein.distance(gt_words, ocr_words)
        gt_word_count = len(gt_words)
        wer = calculate_wer_manual(word_edit, gt_word_count)
        wac = calculate_wac(wer)

        # print("\n--- DEBUG OCR TEXT USED BY EVALUATOR ---")
        # print(ocr_text)
        #
        # print("\n--- DEBUG GT TEXT USED BY EVALUATOR ---")
        # print(gt_text)

        results.append({
            "image": img_id,
            "char_edit": char_edit,
            "char_edit_norm": char_edit_norm,
            "char_ratio": char_ratio,
            "char_ratio_norm": char_ratio_norm,
            "cer": cer,
            "cac": cac,
            "word_edit": word_edit,
            "word_ratio": Levenshtein.ratio(gt_words, ocr_words),
            "wer": wer,
            "wac": wac,
        })

    # Save CSV
    if results:
        keys = results[0].keys()
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"Metrics saved to {output_csv}")
    return results




#=--------------------
def evaluate_postprocessed(folder_path, output_csv="postprocessed_metrics.csv"):
    results = []
    # Loop through cleaned OCR files
    for filename in os.listdir(folder_path):
        if not filename.endswith("postprocessed.txt"):
            continue

        ocr_path = os.path.join(folder_path, filename)

        # Derive base id, e.g. IMG_9163 from IMG_9163_cropped_cleaned_ocr.txt
        img_id = get_img_id(filename)

        # Find matching cleaned GT file in the same folder
        # e.g. IMG_9163_annotation_cleaned_gt.txt
        gt_path = None
        for f in os.listdir(CLEANED_FOLDER_PATH):
            if f.endswith("_cleaned_gt.txt") and get_img_id(f) == img_id:
                gt_path = os.path.join(CLEANED_FOLDER_PATH, f)
                break

        if not gt_path:
            print(f"No cleaned GT found for {filename}")
            continue

        # --- Load OCR cleaned text ---
        ocr_text = load_text(ocr_path)
        ocr_norm = normalize_for_char_metric(ocr_text)
        ocr_words = load_words(ocr_path)

        # --- Load GT cleaned text ---
        gt_text = load_text(gt_path)
        gt_norm = normalize_for_char_metric(gt_text)
        gt_words = load_words(gt_path)

        # --- Character-level metrics
        # ---
        char_edit = Levenshtein.distance(gt_text, ocr_text)
        char_edit_norm = Levenshtein.distance(gt_norm, ocr_norm)
        char_ratio = Levenshtein.ratio(gt_text, ocr_text)
        char_ratio_norm = Levenshtein.ratio(gt_norm, ocr_norm)

        cer = calculate_cer_manual(char_edit_norm, gt_norm)
        cac = calculate_cac(cer)

        # --- Word-level metrics ---
        word_edit = Levenshtein.distance(gt_words, ocr_words)
        gt_word_count = len(gt_words)
        wer = calculate_wer_manual(word_edit, gt_word_count)
        wac = calculate_wac(wer)

        # print("\n--- DEBUG OCR TEXT USED BY EVALUATOR ---")
        # print(ocr_text)
        #
        # print("\n--- DEBUG GT TEXT USED BY EVALUATOR ---")
        # print(gt_text)

        results.append({
            "image": img_id,
            "char_edit": char_edit,
            "char_edit_norm": char_edit_norm,
            "char_ratio": char_ratio,
            "char_ratio_norm": char_ratio_norm,
            "cer": cer,
            "cac": cac,
            "word_edit": word_edit,
            "word_ratio": Levenshtein.ratio(gt_words, ocr_words),
            "wer": wer,
            "wac": wac,
        })

    # Save CSV
    if results:
        keys = results[0].keys()
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"Metrics saved to {output_csv}")
    return results




# def each_word_on_new_line(input_folder_path, output_folder_path):
#     with open(input_folder_path, "r", encoding="utf-8") as f:
#         text = f.read()
#     words = text.split()
#     cleaned = [w.strip() for w in words if w.strip()]
#     with open(output_folder_path, "w", encoding="utf-8") as f:
#         for word in cleaned:
#             f.write(word + "\n")

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

# for processing  multiple files in a folder
# def postprocess_text(input_folder,output_folder):
#     """function to spell check words in extracted text,
#     find candidates for correction, correct words
#     :param input_folder: folder containing extracted text
#     :param output_folder: folder where results will be saved as a .txt file"""
#     os.makedirs(output_folder, exist_ok=True) #create output folder
#     # candidates_csv_path = os.path.join(output_folder, "candidates.csv")
#     candidates_csv_path = os.path.join(output_folder, "candidates_updated_dict.csv")
#     with open(candidates_csv_path, "w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["filename", "misspelt_word", "candidates"])
#         for filename in os.listdir(input_folder):
#             if not filename.endswith("_cleaned_ocr.txt"):
#                 continue
#             loaded_txt_text = load_words(os.path.join(input_folder, filename))
#             misspelt = spell.unknown(loaded_txt_text) # find and store misspelt words in the loaded text
#             num_of_wrong_words = len(misspelt)
#             print(f"filename: {filename}")
#             print(f"Found {num_of_wrong_words} misspelled words in {filename}")
#             for word in misspelt:
#                 candidates = spell.candidates(word)
#                 if candidates is None:
#                     candidates_str = ""
#                 else:
#                     candidates_str = ",".join(candidates)
#                 print(f" {word}: candidates={candidates}")
#                 writer.writerow([filename, word, candidates_str])
#             # remove misspelt words, and replace it with corrected ones, if no candidate, just add the existing word
#             # ----- correct ------
#             corrected_text =[] #list for tracking corrected words
#             for w in loaded_txt_text: #going through all words in the original text
#                 if w in misspelt: # if the word is misspelt
#                     corrected_text.append(spell.correction(w)) #correct the word and add it to the corrected list
#                 else: corrected_text.append(w) # otherwise add existing to the list
#             # ------ save to txt ------
#             base = filename.replace("_cropped_cleaned_ocr.txt", "")
#             new_filename = f"{base}_postprocessed.txt"
#             out_path = os.path.join(output_folder, new_filename)
#             with open(out_path, "w", encoding="utf-8") as f:
#                 for w in corrected_text:
#                     f.write(w + "\n")

def postprocess_text(input_folder_path, output_folder_path):
    os.makedirs(output_folder_path, exist_ok=True)
    for filename in os.listdir(input_folder_path):
        if not filename.endswith("_cleaned_ocr.txt"):
            continue
        input_path = os.path.join(input_folder_path, filename)
        words = load_words(input_path)
        misspelt = spell.unknown(words)
        print(f"\nFile: {filename}")
        print(f"Found {len(misspelt)} misspelled words")
        print(f"misspelt: {misspelt}")
        corrected_text = []
        for w in words:
            if w in misspelt:
                corrected = spell.correction(w)
                if corrected is None: #if no candidate
                    corrected = w # use existing word
                corrected_text.append(corrected)
            else:
                corrected_text.append(w)
        base = filename.replace("_cropped_cleaned_ocr.txt", "")
        new_filename = f"{base}_postprocessed.txt"
        out_path = os.path.join(output_folder_path, new_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            for w in corrected_text:
                f.write(w + "\n")
        print(f"Saved corrected file to: {out_path}")
    return output_folder_path

def analyse_metrics(csv_in_path, csv_summary_path):
    """function for summarizing the metrics generated, takes a csv file"""
    #open csv, make id into a dataframe
# get an overview of the data: min, max, mean for each col
#count how many of the entries have CER 0.2 or below(good), average: above 0.02 but less than 0.1 and poor: more than 0.1
    #open csv
    df = pd.read_csv(csv_in_path)
    df_copy = df.copy()
    metrics_summary = df_copy.describe()
    #columns
    cer_col = df_copy["cer"]
    cac_col = df_copy["cac"]
    wer_col = df_copy["wer"]
    wac_col = df_copy["wac"]
    w_edit_col = df_copy["word_edit"]
    #benchmark
    good_cer = df_copy[cer_col <= 0.02] # if cer is 2% or less
    avg_cer = df_copy[(cer_col > 0.02) & (cer_col <= 0.1)] # 2-10%
    poor_cer = df_copy[cer_col > 0.1]
    good_wer = df_copy[wer_col <= 0.02]
    avg_wer = df_copy[(wer_col > 0.02) & (wer_col <= 0.1)]
    poor_wer = df_copy[wer_col > 0.1]
    good_word_edit_dist = df_copy[w_edit_col <= 3]
    avg_word_edit_dist = df_copy[(w_edit_col > 3) & (w_edit_col <= 5)]
    poor_word_edit_dist = df_copy[(w_edit_col > 5)]
    excellent_word_edit_dist = df_copy[(w_edit_col <= 1)]
    #how many in each category
    num_good_cer = len(good_cer)
    num_avg_cer = len(avg_cer)
    num_poor_cer = len(poor_cer)
    num_good_wer = len(good_wer)
    num_avg_wer = len(avg_wer)
    num_poor_wer = len(poor_wer)
    num_excellent_word_edit_dist = len(excellent_word_edit_dist)
    num_good_word_edit_dist = len(good_word_edit_dist)
    num_avg_word_edit_dist = len(avg_word_edit_dist)
    num_poor_word_edit_dist = len(poor_word_edit_dist)
    print(f"Summary stats: \n{metrics_summary}\n")
    print(f"Good cer: {good_cer}, avg cer: {avg_cer}, poor cer: {poor_cer}")
    print(f"Num good cer: {num_good_cer}, avg cer: {num_avg_cer}, poor cer: {num_poor_cer}")
    print(f"good wer: {good_wer}, avg wer: {avg_wer}, poor wer: {poor_wer}")
    print(f"num good wer: {num_good_wer}, avg wer: {num_avg_wer}, num poor wer: {num_poor_wer}")
    print(f"excellent word edit dist count: {num_excellent_word_edit_dist}, good word edit dist count: {num_good_word_edit_dist}, avg edit dist count: {num_avg_word_edit_dist}, poor word edit dist count: {num_poor_word_edit_dist}")
    analysis_dict = {
        "mean_cer": cer_col.mean(),
        "min_cer": cer_col.min(),
        "max_cer": cer_col.max(),
        "mean_wer": wer_col.mean(),
        "min_wer": wer_col.min(),
        "max_wer": wer_col.max(),
        "mean_cac": cac_col.mean(),
        "mean_wac": wac_col.mean(),
        "mean_word_edit": w_edit_col.mean(),
        "min_word_edit": w_edit_col.min(),
        "max_word_edit": w_edit_col.max(),
        # --- CER categories ---
        "num_good_cer": num_good_cer,
        "num_avg_cer": num_avg_cer,
        "num_poor_cer": num_poor_cer,
        # --- WER categories ---
        "num_good_wer": num_good_wer,
        "num_avg_wer": num_avg_wer,
        "num_poor_wer": num_poor_wer,
        # --- Word edit distance categories ---
        "num_excellent_word_edit": num_excellent_word_edit_dist,
        "num_good_word_edit": num_good_word_edit_dist,
        "num_avg_word_edit": num_avg_word_edit_dist,
        "num_poor_word_edit": num_poor_word_edit_dist,
        # --- Total samples ---
        "total_samples": len(df_copy)
    }
    analysis_df = pd.DataFrame.from_dict(analysis_dict, orient="index", columns=["value"])
    summary = df_copy.describe().T
    summary.insert(0, "metric", summary.index)
    with open(csv_summary_path, "w", encoding="utf-8") as f:
        summary.to_csv(f)
        f.write(f"summary stats")
        summary.to_csv(f, index=False)
    print(f"Analysis summary saved to {csv_summary_path}")


