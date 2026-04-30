import image_utils as img
import ocr_utils as ocr
import text_utils as txt
# import eval_utils_copy as eval
import eval_utils_copy_postp_return_filepath_not_folder as eval
from config_refactor import (JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER,
                             CLEANED_FOLDER_PATH, POSTPROCESS_OUT_FOLDER,
                             PREPROCESSED_CSV_PATH, POSTPROCESSED_CSV_PATH,
                             SUMMARY_PREPROC_PATH, SUMMARY_POSTPROC_PATH,
                             CLEANED_2, CANDIDATE_WORDS_PATH, EXCLUDE_WORDS_PATH, PB_COUNT_CSV_PATH)
import os
import Levenshtein
# import postprocess_utils as postp
import postprocess_utils_return_filepath as postp
import pb_checker as pb
import messaging_utils as msg


def preprocess_image(image_path): # running img tasks
    filename = os.path.basename(image_path) # extract filename from full file path
    extension = filename.lower().split(".")[-1] # get the extension(heic)
    if extension == "heic": # if it's heic, which is most probably, for an img taken with my iphone
        jpg_filepath = img.heic_to_jpg(image_path, JPG_OUTPUT_FOLDER)  # HEIC conversion: convert heic to jpg extension
    else:# otherwise
        jpg_filepath = image_path # use the existing path which becomes jpg path
    gscale_img_path = img.colour_to_greyscale(jpg_filepath, GREYSCALE_FOLDER) # greyscale conversion: colour to grey
    return gscale_img_path # return the grey image filepath

# --------- perform ocr on cropped img, clean, evaluate

def process_cropped_image(cropped_img_path):
    ocr_extracted = ocr.perform_ocr_on_single_image(cropped_img_path) # ocr text extraction
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
    gt_file_path = txt.find_matching_gt_file(ocr_extracted)  # find corresponding gt text
    if not gt_file_path:
        print("No matching GT file found.")
        return
    gt_before = txt.load_text(gt_file_path)
    gt_before_w = txt.load_words(gt_file_path)
    print("\n--- GT TEXT BEFORE CLEANING ---")
    # print(gt_before)
    # print("GT words:", gt_before_w)

    cleaned_gt_path = txt.count_word_and_char(gt_file_path, file_type="gt")  # clean gt text
    cleaned_extracted_path = txt.count_word_and_char(ocr_extracted, file_type="ocr") #clean ocr text
    print(f"debug {cleaned_gt_path}")
    print(f" debug CLEANED_FOLDER_PATH: {CLEANED_FOLDER_PATH}")
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

    preprocessed_evaluated_result = eval.evaluate_preprocessed(cleaned_extracted_path,
        CLEANED_FOLDER_PATH,
        "preprocessed_metrics_single.csv"
    )
    # return preprocessed_evaluated_result
    print(f" ------------ preprocessing done")
    print(f"preprocessed evaluated - result: {preprocessed_evaluated_result}")
    postprocessed_text_path = postp.postprocess_text(cleaned_extracted_path,POSTPROCESS_OUT_FOLDER)
    print(f" ------------ postprocessing done")
    postprocessed_evaluated_result = eval.evaluate_postprocessed(postprocessed_text_path, "postprocessed_metrics_single.csv")
    print(f" postprocessed evaluated - result: {postprocessed_evaluated_result}")
    print(f"preprocessed metrics summary: ")
    eval.analyse_metrics(PREPROCESSED_CSV_PATH, SUMMARY_PREPROC_PATH)
    print(f"postprocessed metrics summary: ")
    eval.analyse_metrics(POSTPROCESSED_CSV_PATH, SUMMARY_POSTPROC_PATH)
    # words_per_line_folder_path = txt.each_word_on_new_line(CLEANED_FOLDER_PATH, CLEANED_2)
    pb.is_it_plant_based(cleaned_extracted_path,EXCLUDE_WORDS_PATH)
    pb.count_pb_identified(CLEANED_FOLDER_PATH, EXCLUDE_WORDS_PATH,PB_COUNT_CSV_PATH)
