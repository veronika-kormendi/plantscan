# folder paths
INPUT_FOLDER = 'G:\\My Drive\\plantscan_photos_to_process' # input_image_folder_path for heitc_to_jpg() function
JPG_OUTPUT_FOLDER = 'G:\\My Drive\\plantscan_photos_to_process\\jpg_folder2_single' # output_folder_path for heic_to_jpg() function
GREYSCALE_FOLDER = 'G:\\My Drive\\plantscan_photos_to_process\\gscale_folder2_single' # output_folder_path for gscale images
CROPPED_FOLDER = 'G:\\My Drive\\plantscan_photos_to_process\\cropped_images_folder2_single' # cropped images to be saved here
CLEANED_FOLDER_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\cleaned_folder_single' #new folder for cleaned files
ANNOTATION_FOLDER = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\annotation' # annotated text files can be found here
CLEANED_2 = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\word_per_line_single'
POSTPROCESS_OUT_FOLDER = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\postprocessed_single'
CANDIDATE_WORDS_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\refactor_single'
PREPROCESSED_CSV_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\preprocessed_metrics_single.csv'
POSTPROCESSED_CSV_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\postprocessed_metrics_single.csv'
SUMMARY_PREPROC_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\preprocessed_summary_single.csv'
SUMMARY_POSTPROC_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\postprocessed_summary_single.csv'
EXCLUDE_WORDS_PATH = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\exclude_list.csv'
# GUI settings
WINDOW_TITLE = "is_it_plant_based?"
THEME = "vapor"
ICON_PATH = 'C:\\Users\\veron\\Downloads\\isitpb.ico'
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


