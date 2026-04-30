import os # for file handling
from PIL import Image, ImageTk  # for managing images
import pillow_heif # for HEIC to JPG conversion
import cv2 as cv # openCV
from config_refactor import DEFAULT_RESIZE_WIDTH

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

def colour_to_greyscale(coloured_img_path, output_path): #takes image path
    os.makedirs(output_path, exist_ok=True)  # make folder & don't throw error if already exist
    filename = os.path.basename(coloured_img_path)
    gscale_output_path = os.path.join(output_path, filename)
    coloured_img = cv.imread(coloured_img_path)  # read image
    if coloured_img is None:
        print(f"could not read image:{coloured_img}")
        return None
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY)  # turn it to greyscale
    cv.imwrite(gscale_output_path, greyscale_img)  # save gscale img to the gscale output folder
    print(f"Greyscale conversion successful: {filename} is greyscale now.")
    return gscale_output_path

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
