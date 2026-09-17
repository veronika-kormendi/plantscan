import os
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')

# folder paths
INPUT_FOLDER = os.getenv("INPUT_FOLDER") # input_image_folder_path for heitc_to_jpg() function
JPG_OUTPUT_FOLDER = os.getenv("JPG_OUTPUT_FOLDER") # output_folder_path for heic_to_jpg() function
GREYSCALE_FOLDER = os.getenv("GREYSCALE_FOLDER") # output_folder_path for gscale images
CROPPED_FOLDER = os.getenv("CROPPED_FOLDER") # cropped images to be saved here
CLEANED_FOLDER_PATH = os.getenv("CLEANED_FOLDER_PATH") #new folder for cleaned files
ANNOTATION_FOLDER = os.getenv("ANNOTATION_FOLDER") # annotated text files can be found here
CLEANED_2 = os.getenv('CLEANED_2')
POSTPROCESS_OUT_FOLDER = os.getenv('POSTPROCESS_OUT_FOLDER')
CANDIDATE_WORDS_PATH = os.getenv('CANDIDATE_WORDS_PATH')
PREPROCESSED_CSV_PATH = os.getenv('PREPROCESSED_CSV_PATH')
POSTPROCESSED_CSV_PATH = os.getenv('POSTPROCESSED_CSV_PATH')
SUMMARY_PREPROC_PATH = os.getenv('SUMMARY_PREPROC_PATH')
SUMMARY_POSTPROC_PATH = os.getenv('SUMMARY_POSTPROC_PATH')
EXCLUDE_WORDS_PATH = os.getenv('EXCLUDE_WORDS_PATH')
PB_COUNT_CSV_PATH = os.getenv('PB_COUNT_CSV_PATH')
FOLDER_TO_WATCH = os.getenv('FOLDER_TO_WATCH')
# GUI settings
WINDOW_TITLE = "is_it_plant_based?"
THEME = "vapor"
ICON_PATH = os.getenv("ICON_PATH")
DEFAULT_RESIZE_WIDTH = 600
CROP_SHIFT = 12
# File dialog settings
SUPPORTED_IMAGE_TYPES = [
    ("Supported image files", "*.jpg *.jpeg *.heic *.HEIC")
]
# OCR settings
OCR_SETTINGS = {
    "use_doc_orientation_classify": True,
    "use_doc_unwarping": False,
    "use_textline_orientation": False,
}


