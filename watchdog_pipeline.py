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
import os
import Levenshtein
# import postprocess_utils as postp
import postprocess_utils_return_filepath as postp
import pb_checker as pb
import messaging_utils as msg



def preprocess_cropped_image(image_path):
    """takes the newly uploaded image and start preprocessing: heic to jpg, greyscale conversion"""
