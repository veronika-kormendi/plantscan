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
input_folder = 'G:\\My Drive\\plantscan_photos_to_process' # input_image_folder_path for heitc_to_jpg() function
jpg_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\jpg_folder2' # output_folder_path for heic_to_jpg() function
greyscale_folder = 'G:\\My Drive\\plantscan_photos_to_process\\gscale_folder2' # output_folder_path for gscale images
cropped_folder = 'G:\\My Drive\\plantscan_photos_to_process\\cropped_images_folder2' # cropped images to be saved here
cleaned_folder_path = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\cleaned_folder_test2' #new folder for cleaned files

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title("is_it_plant_based?") # add gui window title
gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
style_obj = ttk.Style(theme="vapor") # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

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

def colour_to_greyscale(input_folder, coloured_img, output_path):
    """turn coloured image into greyscale image
    :param input_folder: input image's folder path
    :param coloured_img: coloured image
    :param output_folder_path: the folder where the greyscale image is saved
    :return: the filepath of the greyscale image"""
    # path = join input folder & selected coloured image
    input_img_path = os.path.join(input_folder, coloured_img) # image to greyscale
    if not os.path.exists(output_path): # if folder does not exist
        os.makedirs(output_path, exist_ok=True) # make folder & don't throw error if already exist
    gscale_output_filepath = os.path.join(output_path, coloured_img) # build path where to save the gscale img
    gscale_filename = os.path.basename(gscale_output_filepath) # get the gscale filename
    coloured_img = cv.imread(input_img_path) # read image
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY) # turn it to greyscale
    cv.imwrite(gscale_output_filepath, greyscale_img) # save gscale img to the gscale output folder
    print(f"Greyscale conversion successful: {gscale_filename} is greyscale now.")
    return gscale_output_filepath

def select_img_from():
    """Select an image from the input folder to start the pipeline.
    :returns: filepath of the image to be opened i.e. selected file"""
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=(("Supported image files", "*.jpg *.heic *.HEIC *.jpeg"),))
    if not file_to_open:
        return None
    return file_to_open

def resize_image(image, new_w=600):
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

def display_image(tk_img):
    """display image
    :param: tk_img: tk image"""
    global rect_id, start_corner,end_corner, mode, canvas_img_id
    canvas.delete("all")
    rect_id = None
    start_corner = None
    end_corner = None
    mode = None
    canvas_img_id = canvas.create_image(10,10, anchor=tk.NW, image=tk_img) # adding tkinter image to canvas
    canvas.image = tk_img
    print("displaying image", tk_img) # for troubleshooting

def run_img_tasks():
    """run image tasks"""
    global resized_image, output_path
    selected_path = select_img_from() # 1. open img file
    if not selected_path:
        return
    filename = os.path.basename(selected_path)
    extension = filename.lower().split(".")[-1]
    if extension == "heic":
        jpg_filepath = heic_to_jpg(selected_path, jpg_output_folder) # 2. HEIC conversion
        filename = filename.replace('.heic', '.jpg').replace('HEIC', 'jpg')  # replace extension
        output_path = os.path.join(jpg_output_folder, filename)  # add converted file to
    else:
        output_path = os.path.join(jpg_output_folder, filename)
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
    filename = os.path.basename(jpg_filepath)
    gscale_img_path = colour_to_greyscale(jpg_output_folder,filename, greyscale_folder) # 3. greyscale conversion
    pil_img = Image.open(gscale_img_path)
    resized_image = resize_image(pil_img)
    tk_img = make_tk_img(resized_image)
    display_image(tk_img)

def draw_rectangle():
    global rect_id
    if start_corner is None or end_corner is None:
        return
    x0, y0 = start_corner
    x1, y1 = end_corner
    if rect_id is None:
        rect_id = canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)  # create rectangle
    else:
        canvas.coords(rect_id, x0, y0, x1, y1)

def get_rect_coords():
    if rect_id is None:
        return None
    coords = canvas.coords(rect_id)
    if len(coords) !=4:
        return None
    x0, y0, x1, y1 = coords
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    return x0, y0, x1, y1

def is_click_in_rect(x, y):
    rect_coords = get_rect_coords()
    if rect_coords is None:
        return False
    x0, y0, x1, y1 = rect_coords
    return x0 <= x <= x1 and y0 <= y <= y1

def on_click(event):
    global start_corner, end_corner, rect_id, mode, offset_x, offset_y
    if rect_id is None: # scenario 1 - if rectangle does not exist
        mode = "drawing"
        # start drawing the rectangle
        start_corner = (event.x, event.y)  # drag point - drag starts here
        end_corner = (event.x, event.y)  # release point - drag ends here
        draw_rectangle() #display rectangle with start_corner dragged to end corner
        return
    # scenario 2 - rectangle exists,  so check if click is inside the rect
    if is_click_in_rect(event.x, event.y): # if click is inside the rect, drag it
        mode = "moving" # we want to move the existing rect
        x0, y0, x1, y1 = canvas.coords(rect_id)
        offset_x = event.x - x0
        offset_y = event.y - y0
        return
    # scenario 3 - when click is outside of rect - draw a new rectangle
    canvas.delete(rect_id)
    rect_id = None # reset
    mode = "drawing"
    start_corner = (event.x, event.y)
    end_corner = (event.x, event.y)
    draw_rectangle()

def drag_rect(event):
    global end_corner
    if mode == "drawing":
        end_corner = (event.x, event.y)
        draw_rectangle()
    elif mode == "moving":
        x0,y0,x1,y1= canvas.coords(rect_id)
        dx = event.x - (x0+offset_x)
        dy = event.y - (y0+offset_y)
        canvas.move(rect_id, dx, dy)

def on_release(event): # when mouse is released
    global mode
    mode = None

def shift_coords(x0,y0,x1,y1):
    """shift the crop rectangle coordinates on the canvas from left top corner"""
    return x0-12,y0-12, x1-12, y1-12

def save_cropped_img():
    """save cropped image
    """
    global resized_image, output_path
    if resized_image is None:
        print("No image loaded.")
        return
    if output_path is None:
        print("No output path was provided.")
        return
    rect = get_rect_coords()
    if rect is None:
        print("No rectangle drawn.")
        return
    # canvas coords to image coords since
    # rectangle is in canvas coords & cropped img is in other coords
    x0, y0, x1, y1 = shift_coords(*canvas.coords(rect_id))
    cropped = resized_image.crop((x0, y0, x1, y1))
    if not os.path.exists(cropped_folder): #if it does not exist
        os.makedirs(cropped_folder) # create cropped folder
    original_name = os.path.basename(output_path) #original name
    base, _ = os.path.splitext(original_name)
    new_name = f"{base}_cropped.jpg"
    save_path = os.path.join(cropped_folder, new_name) # where to save the new one
    if save_path:
        cropped.save(save_path, format="JPEG")
        print(f"Saved cropped image ({os.path.basename(save_path)}) to {save_path}.") # Saved cropped image (IMG_7476_cropped.jpg) to
    return save_path

def perform_ocr_multiple(img_path, ocr_output_folder_path="extracted_text_folder2"):
    os.makedirs("output2", exist_ok=True)
    os.makedirs(ocr_output_folder_path, exist_ok=True) # create folder
    ocr = PaddleOCR(use_doc_orientation_classify=True, #create ocr object
                    use_doc_unwarping=False,
                    use_textline_orientation=False,)
    # go through the files in the cropped folder //called later
    for img_file in os.listdir(img_path):
        ocr_path = os.path.join(img_path, img_file) # get cropped image
        result_list = ocr.predict(ocr_path) # create results & run ocr
        print(f"result length, {len(result_list)}.")
        for res in result_list:
            res.print()
            res.save_to_json("output2")
            res.save_to_img("output2")
            print(f"preforming ocr on {img_file}.")
    for json_file in os.listdir("output2"):
        if not json_file.endswith(".json"):
            continue
        json_path = os.path.join(os.path.join("output2", json_file))
        base = os.path.splitext(json_file)[0] # IMG_0000_cropped_res
        txt_path = os.path.join(ocr_output_folder_path, f"{base}.txt")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        text_lines = data.get("rec_texts", [])
        with open(txt_path, "w", encoding="utf-8") as f:
            for line in text_lines:
                f.write(line + "\n")
    print("ORC Finished.")
    print(ocr_output_folder_path)
    return ocr_output_folder_path  # return the folder path where extracted texts saved

def save_crop_and_start_ocr():
    #1. save cropped image
    cropped_img_path = save_cropped_img()
    print(f"Saved cropped image to {cropped_img_path}.")
    if cropped_img_path is None:
        return
    #2. extract text
    ocr_extracted = perform_ocr_multiple(cropped_folder)
    # open extracted text files from extracted texts folder path
    for root, dirs, files in os.walk(ocr_extracted):  # go through the content of the folder and
        for file in files:  # for every file
            file_path = os.path.join(root, file)
            print(f"file {file}")  # print the file path
            display_extracted = load_words(file_path)
            print(f"ocr text before cleaning: {display_extracted}")
            cleaned_extracted = count_word_and_char(file_path)
            display_cleaned_extracted = load_words(cleaned_extracted)
            print(f"ocr text after cleaning: {display_cleaned_extracted}")

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

def count_word_and_char(text_file, file_type="ocr"):
    """
    Cleans the text, counts the number of words and chars in a text file.
    :param text_file:
    :return: cleaned text path
    """
    word_count = 0
    char_count = 0
    cleaned_lines =[]
    if not os.path.exists(cleaned_folder_path):
        os.makedirs(cleaned_folder_path)
    origin = os.path.basename(text_file)
    without_extension = os.path.splitext(origin)[0]
    # cleaned_filename = f"{without_extension}_cleaned_super.txt"
    if file_type == "gt":
        cleaned_filename = f"{without_extension}_cleaned_gt.txt"
    else:
        cleaned_filename = f"{without_extension}_cleaned_ocr.txt"
    cleaned_path = os.path.join(cleaned_folder_path, cleaned_filename)
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
    print(f"There are {word_count} words and {char_count} chars in the file {text_file}\n")
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


# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
select_img_btn = tk.Button(gui_window, text="Select Image", padx=10, pady=2, command=run_img_tasks)
select_img_btn.pack(pady=6)
# save_btn = tk.Button(gui_window, text="Save Crop", command=save_cropped_img)
save_btn = tk.Button(gui_window, text="Save Crop",  padx=10, pady=2,command=save_crop_and_start_ocr)
save_btn.pack()
canvas.pack()
gui_window.mainloop() # displaying the window & listen for events






