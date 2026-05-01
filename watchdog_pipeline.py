# new pipeline for folder watcher execution flow
#start
# user uploads cropped HEIc image to the folder to watch
#new filee added triggers the execution flow of the following:
# heic to jpg
#greyscale
#ocr extraction
#pb_checker
#send result
#end

import image_utils as img
import ocr_utils as ocr
import text_utils as txt
# import eval_utils_copy as eval
import eval_utils_copy_postp_return_filepath_not_folder as eval
from config_refactor import (JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER,
                             CLEANED_FOLDER_PATH, POSTPROCESS_OUT_FOLDER,
                             PREPROCESSED_CSV_PATH, POSTPROCESSED_CSV_PATH,
                             SUMMARY_PREPROC_PATH, SUMMARY_POSTPROC_PATH,
                             CLEANED_2, CANDIDATE_WORDS_PATH, EXCLUDE_WORDS_PATH, PB_COUNT_CSV_PATH, SLACK_CHANNEL_ID)
import postprocess_utils_return_filepath as postp
import pb_checker as pb
import messaging_utils as msg



def preprocess_cropped_image(image_path):
    """takes the newly uploaded image and start preprocessing: heic to jpg, greyscale conversion"""
    jpg_img_path = img.heic_to_jpg(image_path,JPG_OUTPUT_FOLDER) # heic to jpg conversion
    gscale_path = img.colour_to_greyscale(jpg_img_path, GREYSCALE_FOLDER) # convert to greyscale
    print(f" ------------ preprocessing done")
    return gscale_path


def process_cropped_image(gscale_path):
    """takes the gscale img path to further process it: ocr, postprocess, analyse, send result"""
    ocr_extracted = ocr.perform_ocr_on_single_image(gscale_path)  # ocr text extraction
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
    print(gt_before)
    print("GT words:", gt_before_w)

    cleaned_gt_path = txt.count_word_and_char(gt_file_path, file_type="gt")  # clean gt text
    cleaned_extracted_path = txt.count_word_and_char(ocr_extracted, file_type="ocr")  # clean ocr text
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
    #------comment this out for new images - no annotated text--------
    # preprocessed_evaluated_result = eval.evaluate_preprocessed(cleaned_extracted_path,
    #                                                            CLEANED_FOLDER_PATH,
    #                                                            "preprocessed_metrics_watchdog.csv"
    #                                                            )
    # # return preprocessed_evaluated_result
    # print(f"preprocessed evaluated - result: {preprocessed_evaluated_result}")
    # postprocessed_text_path = postp.postprocess_text(cleaned_extracted_path, POSTPROCESS_OUT_FOLDER)
    # print(f" ------------ postprocessing done")
    # postprocessed_evaluated_result = eval.evaluate_postprocessed(postprocessed_text_path,
    #                                                              "postprocessed_metrics_watchdog.csv")
    # print(f" postprocessed evaluated - result: {postprocessed_evaluated_result}")
    # print(f"preprocessed metrics summary: ")
    # eval.analyse_metrics(PREPROCESSED_CSV_PATH, SUMMARY_PREPROC_PATH)
    # print(f"postprocessed metrics summary: ")
    # eval.analyse_metrics(POSTPROCESSED_CSV_PATH, SUMMARY_POSTPROC_PATH)
    #----------commented out end-----------------
    # words_per_line_folder_path = txt.each_word_on_new_line(CLEANED_FOLDER_PATH, CLEANED_2)
    # pb_result = pb.is_it_plant_based(cleaned_extracted_path,EXCLUDE_WORDS_PATH)
    # pb.count_pb_identified(CLEANED_FOLDER_PATH, EXCLUDE_WORDS_PATH,PB_COUNT_CSV_PATH)
    # msg.send_slack_message(f"isItPlantBased? result: {pb_result}", SLACK_CHANNEL_ID)
    is_pb, matched_word = pb.is_it_plant_based(cleaned_extracted_path, EXCLUDE_WORDS_PATH)
    if is_pb:  # if it is plant-based, tailor message accordingly
        result_message = f"This product is plant-based."
    else:  # non-plant-based scenario
        result_message = f"Sorry, not a plant-based product. It contains {matched_word}."
    pb.count_pb_identified(CLEANED_FOLDER_PATH, EXCLUDE_WORDS_PATH, PB_COUNT_CSV_PATH)
    msg.send_slack_message(f"isItPlantBased? result: {result_message}", SLACK_CHANNEL_ID)
