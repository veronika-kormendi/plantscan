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

start_corner = None
end_corner = None
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

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title("is_it_plant_based?") # add gui window title
gui_window.iconbitmap('C:\\Users\\veron\\Downloads\\isitpb.ico') # adding icon to gui window
style_obj = ttk.Style(theme="vapor") # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset

# step 1 - img conversion: HEIC to JPG
input_folder = 'G:\\My Drive\\plantscan_photos_to_process'
output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\to_jpg'

# open & save HEIC to JPG img
def heic_to_jpg(input_path):
    pillow_heif.register_heif_opener() # to be able to open HEIC files
    if not os.path.exists(output_folder): # if output folder does not exist
        os.makedirs(output_folder) # create one
    filename = os.path.basename(input_path)
    jpg_filename = f"{os.path.splitext(filename)[0]}.jpg" # build jpg filename
    jpg_path = os.path.join(output_folder, jpg_filename) #build jpg path where to save the jpg img
    try:
        img = Image.open(input_path)  # open img from input path
        img.save(jpg_path, format='JPEG') # save jpg
    except Exception as e: # error handling
        print(f"Heic conversion error occurred: {e}")
        return
    print(f"File extension changed from {filename} to JPG")

# ------- GREYSCALE ----------
greyscale_output_folder = 'G:\\My Drive\\plantscan_photos_to_process\\new_test'
def colour_to_greyscale(coloured_img):
    # path = join input folder & selected coloured image
    img_to_greyscale = os.path.join(output_folder, coloured_img)
    if not os.path.exists(greyscale_output_folder):
        os.makedirs(greyscale_output_folder)
    gscale_output = os.path.join(greyscale_output_folder, coloured_img)
    gscale_filename = os.path.basename(gscale_output)
    coloured_img = cv.imread(img_to_greyscale)
    greyscale_img = cv.cvtColor(coloured_img, cv.COLOR_BGR2GRAY) #convert to gscale
    cv.imwrite(gscale_output, greyscale_img) # saving the greyscale image to the output folder
    print(f"Greyscale conversion successful: {gscale_filename} is greyscale now.")

# open image file - JPG
def select_img_from():
    file_to_open = filedialog.askopenfilename(title="Select Image", filetypes=(("Supported image files", "*.jpg *.heic *.HEIC *.jpeg"),))
    if not file_to_open: # if the file does not exist
        return None
    # opened_pil_img = Image.open(file_to_open)
    # return opened_pil_img # returns PIL image
    return file_to_open # return filepath

# resize image proportionately to fit to screen
def resize_image(image, new_w=600):
    img_w, img_h = image.size
    new_h = int(img_h * new_w / img_w)
    resized_image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return resized_image

# turn image opened with PIL to tk compatible image
def make_tk_img(resized_image):
    tk_img = ImageTk.PhotoImage(resized_image)
    return tk_img

def display_image(tk_img):
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
    global resized_image, output_path
    selected_path = select_img_from() # open img file
    if not selected_path:
        return
    filename = os.path.basename(selected_path)
    extension = filename. lower().split('.')[-1]
    if extension == "heic":
        heic_to_jpg(selected_path) # convert heic to jpg
        filename = filename.replace('.heic', '.jpg').replace('HEIC', 'jpg') # replace extension
        output_path = os.path.join(output_folder, filename) #add converted file to
    else:
        output_path = os.path.join(output_folder, filename)
        if not os.path.exists(output_path):
            os.makedirs(output_folder, exist_ok=True)
    colour_to_greyscale(os.path.basename(output_path)) # turn into greyscale
    gscale_path = os.path.join(greyscale_output_folder, os.path.basename(output_path))
    pil_img = Image.open(gscale_path) # load image
    resized_image = resize_image(pil_img)  #resize image
    tk_img = make_tk_img(resized_image) # convert to tk img
    display_image(tk_img) # display

# ----- BUTTON ---------
select_img_btn = tk.Button(gui_window, text="Select Image", padx=10, pady=2, command=run_img_tasks)
select_img_btn.pack()

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
    return x0-12,y0-12, x1-12, y1-12

cropped_folder = 'G:\\My Drive\\plantscan_photos_to_process\\cropped_images'
def save_cropped_img():
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
    # save_path = filedialog.asksaveasfilename(defaultextension=".png")
    save_path = os.path.join(cropped_folder, new_name) # where to save the new one
    if save_path:
        cropped.save(save_path, format="JPEG")
        print(f"Saved cropped image to {save_path}.")
    return save_path

# def perform_ocr():
#     ocr = PaddleOCR(use_doc_orientation_classify=True,
#                     use_doc_unwarping=True,
#                     use_textline_orientation=True,)
#     result = ocr.predict('G:\\My Drive\\plantscan_photos_to_process\\cropped_images\\IMG_7766_cropped.jpg')
#     for res in result:
#         res.print()
#         res.save_to_img("output")
#         res.save_to_json("output")
#
# perform_ocr()

#process multiple files
# def perform_ocr(folder):
#     ocr = PaddleOCR(use_doc_orientation_classify=True,
#                     use_doc_unwarping=False,
#                     use_textline_orientation=False,)
#     for img_file in os.listdir(folder):
#         ocr_path = os.path.join(folder, img_file)
#         print(f"processing image: {img_file}")
#         result = ocr.predict(cropped_folder)
#         for res in result:
#             res.print()
#             res.save_to_img("output")
#             res.save_to_json("output")
#
# perform_ocr(cropped_folder)




# def perform_ocr_single(img_path):
#     ocr = PaddleOCR(use_doc_orientation_classify=True,
#                          use_doc_unwarping=False,
#                          use_textline_orientation=False,)
#     print(f"Performing OCR on {img_path}...")
#     result = ocr.predict(img_path)
#     base = os.path.splitext(os.path.basename(img_path))[0] # e.g. IMG_8590_cropped
#     # create correct extension
#     json_path = os.path.join("output", f"{base}.json") # for json e.g. IMG_8590_cropped_res.json
#     txt_path = os.path.join("output", f"{base}.txt") # IMG_8590_cropped.txt
#     for res in result:
#         res.print()
#         res.save_to_json(json_path)
#         res.save_to_img("output")
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     text_lines = data.get("rec_texts", [])
#
#     with open(txt_path, "w", encoding="utf-8") as f:
#         for line in text_lines:
#             f.write(line + "\n")
#     print(f"Finished performing OCR on {img_path}.")


def perform_ocr_multiple(img_path): #folder
    ocr = PaddleOCR(use_doc_orientation_classify=True,  #create ocr object
                         use_doc_unwarping=False,
                         use_textline_orientation=False,)
    # go through the files in the cropped folder //called later
    for img_file in os.listdir(img_path):
        ocr_path = os.path.join(img_path, img_file) # get cropped image
        result = ocr.predict(ocr_path) # create results & run ocr
        for res in result:
            res.print()
            res.save_to_json("output")
            res.save_to_img("output")
            print(f"perfoming OCR on {img_file}.")
    for json_file in os.listdir("output"): # extract text from json files
        if  not json_file.endswith(".json"): continue
        json_path = os.path.join(os.path.join("output", json_file))
        base = os.path.splitext(json_file)[0]
        txt_path = os.path.join("output", f"{base}.txt")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        text_lines = data.get("rec_texts", [])
        with open(txt_path, "w", encoding="utf-8") as f:
            for line in text_lines:
                f.write(line + "\n")
    print("ORC Finished.")



def save_and_ocr():
    cropped_img_path = save_cropped_img()
    if cropped_img_path is None:
        return
    perform_ocr_multiple(cropped_folder) # for multiple images
    # perform_ocr_single(cropped_img_path) # for single img


# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
# save_btn = tk.Button(gui_window, text="Save Crop", command=save_cropped_img)
save_btn = tk.Button(gui_window, text="Save Crop", command=save_and_ocr)
save_btn.pack()
canvas.pack()
gui_window.mainloop() # displaying the window & listen for events