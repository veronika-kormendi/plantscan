''' Author: Veronika Kormendi
    Purpose: Final Year Project
'''
# ------- IMPORTS -------
import os
from PIL import Image, ImageTk  # for managing images
import pillow_heif # for HEIC to JPG conversion
import tkinter as tk # for GUI
import cv2 as cv # openCV
import ttkbootstrap as ttk # for modern GUI
from tkinter import filedialog
from paddleocr import PaddleOCR
import json
import string
import unicodedata
import Levenshtein

start_corner = None # start corner of cropping rectangle
end_corner = None # end corner of cropping rectangle
drawn_rect = None
moving_rect = None
rect_id = None
offset_x = None
offset_y = None
mode = None # drawing/moving/none
resized_image = None
output_path = None # working path
rotation_angle = None
canvas_img_id = None
input_folder = 'G:\\My Drive\\plantscan_photos_to_process' # input_path for heic_to_jpg() function
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\jpg_folder' # output_path for heic_to_jpg() function
greyscale_folder = 'G:\\My Drive\\plantscan_photos_to_process\\gscale_folder' # output_path for gscale images

# # ---------- GUI ------------
# gui_window = tk.Tk() # creating a window instance
# gui_window.title("is_it_plant_based?") # add gui window title
# gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
# style_obj = ttk.Style(theme="vapor") # applying theme
# width = gui_window.winfo_screenwidth() # set window width
# height = gui_window.winfo_screenheight() # set window height
# gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

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
    print(f"jpg path: {jpg_path}")
    return jpg_path

def colour_to_greyscale(input_folder, coloured_img, output_folder):
    """turn coloured image into greyscale image
    :param input_folder: input image's folder path
    :param coloured_img: coloured image
    :param output_path: the folder where the greyscale image is saved
    :return: the filepath of the greyscale image"""
    if not os.path.exists(output_folder): # if folder does not exist
        os.makedirs(output_folder, exist_ok=True) # make folder & don't throw error if already exist
    input_path = os.path.join(input_folder, coloured_img) # path = join input folder & selected coloured image
    output_filepath = os.path.join(output_folder, coloured_img) # build the output path where to save the gscale img
    gscale_filename = os.path.basename(output_filepath) # get the gscale filename
    coloured_img = cv.imread(input_path) # read image
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY) # turn it to greyscale
    cv.imwrite(output_filepath, greyscale_img) # save gscale img to the gscale output folder
    print(f"Greyscale conversion successful: {gscale_filename} is greyscale now.")
    return output_filepath

test_input_folder = 'G:\\My Drive\\plantscan_photos_to_process\\converted_to_jpg'
test_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\gscale_folder' # output_path for gscale images
test_file = "IMG_7522.jpg"
test_heic_file = "IMG_7522.HEIC"
jpg_path = heic_to_jpg(os.path.join(input_folder,test_heic_file), output_folder)
colour_to_greyscale(test_input_folder, test_file, test_output_folder)
print(jpg_path)



# def select_img_from():
#     """Select an image from the input folder to start the pipeline.
#     :returns: filepath of the image to be opened i.e. selected file"""
#     file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=(("Supported image files", "*.jpg *.heic *.HEIC *.jpeg"),))
#     if not file_to_open:
#         return None
#     return file_to_open

# def resize_image(image, new_w=600):
#     """Resize an image to a new width and height.
#     :param image: image to be resized
#     :param new_w: new width
#     :returns: resized image"""
#     img_w, img_h = image.size # img width and height
#     new_h = int(img_h * new_w / img_w)
#     resized_image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
#     return resized_image
#
# def make_tk_img(resized_image):
#     """turn image opened with PIL to tk compatible image
#     :param resized_image: resized image
#     :returns: tk_img: tk image"""
#     tk_img = ImageTk.PhotoImage(resized_image)
#     return tk_img
#
# def display_image(tk_img):
#     """display image
#     :param: tk_img: tk image"""
#     global rect_id, start_corner,end_corner, mode, canvas_img_id
#     canvas.delete("all")
#     rect_id = None
#     start_corner = None
#     end_corner = None
#     mode = None
#     canvas_img_id = canvas.create_image(10,10, anchor=tk.NW, image=tk_img) # adding tkinter image to canvas
#     canvas.image = tk_img
#     print("displaying image", tk_img) # for troubleshooting
#
# def run_img_tasks():
#     """run image tasks"""
#     global resized_image, output_path
#     selected_path = select_img_from() # 1. open img file
#     if not selected_path:
#         return
#     filename = os.path.basename(selected_path)
#     extension = filename.lower().split(".")[-1]
#     if extension == "heic":
#         heic_output_path = heic_to_jpg(selected_path, output_folder) # 2. HEIC conversion
#     gscale_img_path = colour_to_greyscale(heic_output_path, greyscale_folder) # 3. greyscale conversion
#     pil_img = Image.open(gscale_img_path)
#     resized_image = resize_image(pil_img)
#     tk_img = make_tk_img(resized_image)
#     display_image(tk_img)








