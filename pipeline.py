import image_utils as img
import ocr_utils as ocr
import text_utils as txt
import postprocess_utils as postp
import evaluation_utils as eval
from config_refactor import JPG_OUTPUT_FOLDER, GREYSCALE_FOLDER
import os

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


# perform ocr on cropped img
def process_cropped_image(cropped_img_path):
    ocr_extracted = ocr.perform_ocr_on_single_image(cropped_img_path)
    if not ocr_extracted:
        print("OCR failed or returned no output.")
        return

