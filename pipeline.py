import image_utils as img
import ocr_utils as ocr
import text_utils as txt
import postprocess_utils as postp
import evaluation_utils as eval
from config_refactor import (JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER,
                             CLEANED_FOLDER_PATH,CLEANED_2, PREPROCESSED_CSV_PATH,
                             SUMMARY_PREPROC_PATH, POSTPROCESSED_CSV_PATH, SUMMARY_POSTPROC_PATH)
import os
import Levenshtein

def preprocess_image(image_path): # running img tasks
    filename = os.path.basename(image_path)
    extension = filename.lower().split(".")[-1]
    if extension == "heic":
        jpg_filepath = img.heic_to_jpg(image_path, JPG_OUTPUT_FOLDER)  # HEIC conversion
        filename = filename.replace('.heic', '.jpg').replace('HEIC', 'jpg')  # replace extension
        output_path = os.path.join(JPG_OUTPUT_FOLDER, filename)  # add converted file to
    else:
        output_path = os.path.join(JPG_OUTPUT_FOLDER, filename)
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
    filename = os.path.basename(jpg_filepath)
    gscale_img_path = img.colour_to_greyscale(JPG_OUTPUT_FOLDER, filename, GREYSCALE_FOLDER) # greyscale conversion
    return gscale_img_path

# --------- perform ocr on cropped img, clean, evaluate
def process_cropped_image(cropped_img_path):
    ocr_extracted = ocr.perform_ocr_on_single_image(cropped_img_path)
    if not ocr_extracted:
        print("OCR failed or returned no output.")
        return
    print(f"OCR performed on: {ocr_extracted}")
    # print ocr & gt text before cleaning
    extracted_before = txt.load_text(ocr_extracted)
    extracted_before_w = txt.load_words(ocr_extracted)
    print("\n--- EXTRACTED TEXT BEFORE CLEANING ---")
    print(extracted_before)
    print(extracted_before_w)
    # --------- find matching GT file (before cleaning)
    gt_file_path = txt.find_matching_gt_file(ocr_extracted)
    if not gt_file_path:
        print("No matching GT file found.")
        return

    gt_before = txt.load_text(gt_file_path)
    gt_before_w = txt.load_words(gt_file_path)

    print("\n--- GT TEXT BEFORE CLEANING ---")
    print(gt_before)
    print("GT words:", gt_before_w)

    # --------- clean text (ocr & gt)
    cleaned_extracted_path = txt.count_word_and_char(ocr_extracted, file_type="ocr")
    cleaned_gt_path = txt.count_word_and_char(gt_file_path, file_type="gt")

    # --------- load & display ocr & gt text
    extracted_after = txt.load_text(cleaned_extracted_path)
    extracted_after_w = txt.load_words(cleaned_extracted_path)
    extracted_norm = txt.normalize_for_char_metric(extracted_after)

    gt_after = txt.load_text(cleaned_gt_path)  # char level
    gt_after_w = txt.load_words(cleaned_gt_path)  # word level
    gt_norm = txt.normalize_for_char_metric(gt_after)

    print("\n--- EXTRACTED TEXT AFTER CLEANING ---")
    print(extracted_after)
    print("OCR extracted words:", extracted_after_w)
    print("\n--- GT TEXT AFTER CLEANING ---")
    print(gt_after)
    print("GT words:", gt_after_w)

    # --------- calculate Levensthein distance and ratios
    print("\n--- METRICS ---")

    # --------- character-level
    char_edit_dist = Levenshtein.distance(gt_after, extracted_after)
    char_edit_dist_norm = Levenshtein.distance(gt_norm, extracted_norm)
    char_ratio = Levenshtein.ratio(gt_after, extracted_after)
    char_ratio_norm = Levenshtein.ratio(gt_norm, extracted_norm)

    print(f"Char edit distance: {char_edit_dist}")
    print(f"Char edit distance (normalized): {char_edit_dist_norm}")
    print(f"Char ratio: {char_ratio}")
    print(f"Char ratio (normalized): {char_ratio_norm}")

    # --------- word-level
    word_edit_dist = Levenshtein.distance(gt_after_w, extracted_after_w)
    word_ratio = Levenshtein.ratio(gt_after_w, extracted_after_w)

    print(f"Word edit distance: {word_edit_dist}")
    print(f"Word ratio: {word_ratio}")

    # --------- calculate WER
    gt_word_count = len(gt_after_w)
    wer_manual = eval.calculate_wer_manual(word_edit_dist, gt_word_count)
    print(f"WER (manual): {wer_manual}")
    # calculate CER
    cer = eval.calculate_cer_manual(char_edit_dist_norm, gt_norm)
    print(f"CER (manual): {cer}")

    # --------- word & char accuracy calculations
    wac = eval.calculate_wac(wer_manual)
    wac_rounded = round(wac, 2) * 100
    print(f"WAC: {wac}, rounded: {wac_rounded}%")
    cac = eval.calculate_cac(cer)
    cac_rounded = round(cac, 2) * 100
    print(f"CAC: {cac}, rounded: {cac_rounded}%")

words_per_line_folder_path = txt.each_word_on_new_line(CLEANED_FOLDER_PATH, CLEANED_2)
print(f"preprocessed metrics summary: ")
eval.analyse_metrics(PREPROCESSED_CSV_PATH,SUMMARY_PREPROC_PATH)
print(f"postprocessed metrics summary: ")
eval.analyse_metrics(POSTPROCESSED_CSV_PATH, SUMMARY_POSTPROC_PATH)