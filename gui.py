import tkinter as tk # for GUI
import ttkbootstrap as ttk # for modern GUI
from config import *
import os
from PIL import Image, ImageTk  # for managing images
from utils import select_img_from, heic_to_jpg, colour_to_greyscale, resize_image, make_tk_img, \
    perform_ocr_on_single_image, load_words, load_text, count_word_and_char, normalize_for_char_metric,\
    load_and_clean_char, find_matching_gt_file
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

# ---------- GUI ------------
gui_window = tk.Tk() # creating a window instance
gui_window.title(WINDOW_TITLE) # add gui window title
gui_window.iconbitmap(ICON_PATH) # adding icon to gui window
style_obj = ttk.Style(theme=THEME) # applying theme
width = gui_window.winfo_screenwidth() # set window width
height = gui_window.winfo_screenheight() # set window height
gui_window.geometry(f"{width}x{height}+0+0") # window size with width, height, offset, offset


def display_image(tk_img):
    """display image
    :param: tk_img: tk image"""
    global rect_id, start_corner, end_corner, mode, canvas_img_id
    canvas.delete("all")
    rect_id = None
    start_corner = None
    end_corner = None
    mode = None
    canvas_img_id = canvas.create_image(10, 10, anchor=tk.NW, image=tk_img)  # adding tkinter image to canvas
    canvas.image = tk_img
    print("displaying image", tk_img)  # for troubleshooting

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
    return x0-CROP_SHIFT,y0-CROP_SHIFT, x1-CROP_SHIFT, y1-CROP_SHIFT

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
    if not os.path.exists(CROPPED_FOLDER): #if it does not exist
        os.makedirs(CROPPED_FOLDER) # create cropped folder
    original_name = os.path.basename(output_path) #original name
    base, _ = os.path.splitext(original_name)
    new_name = f"{base}_cropped.jpg"
    save_path = os.path.join(CROPPED_FOLDER, new_name) # where to save the new one
    if save_path:
        cropped.save(save_path, format="JPEG")
        print(f"Saved cropped image ({os.path.basename(save_path)}) to {save_path}.") # Saved cropped image (IMG_7476_cropped.jpg) to
    return save_path

def run_img_tasks():
    """run image tasks"""
    global resized_image, output_path
    selected_path = select_img_from()  # 1. open img file
    if not selected_path:
        return
    filename = os.path.basename(selected_path)
    extension = filename.lower().split(".")[-1]
    if extension == "heic":
        jpg_filepath = heic_to_jpg(selected_path, JPG_OUTPUT_FOLDER)  # 2. HEIC conversion
        filename = filename.replace('.heic', '.jpg').replace('HEIC', 'jpg')  # replace extension
        output_path = os.path.join(JPG_OUTPUT_FOLDER, filename)  # add converted file to
    else:
        output_path = os.path.join(JPG_OUTPUT_FOLDER, filename)
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
    filename = os.path.basename(jpg_filepath)
    gscale_img_path = colour_to_greyscale(JPG_OUTPUT_FOLDER, filename, GREYSCALE_FOLDER)  # 3. greyscale conversion
    pil_img = Image.open(gscale_img_path)
    resized_image = resize_image(pil_img)
    tk_img = make_tk_img(resized_image)
    display_image(tk_img)

# def process_cropped_img():
#     #1. save cropped image
#     cropped_img_path = save_cropped_img()
#     print(f"Saved cropped image to {cropped_img_path}.")
#     if cropped_img_path is None:
#         return
#     #2. extract text
#     ocr_extracted = perform_ocr_on_single_image(cropped_img_path)
#     if ocr_extracted is not None:
#         print(f"ocr performed on: {ocr_extracted}") #display the current text file
#         load_extracted_txt = load_text(ocr_extracted) # 1. load
#         cleaned_extracted = count_word_and_char(ocr_extracted,file_type="ocr") # 2. clean
#         load_cleaned_extracted = load_text(cleaned_extracted) # 3. load cleaned one
#         print(f"extracted before cleaning: {load_extracted_txt}")
#         print(f"extracted after cleaning: {load_cleaned_extracted}")
#
#         # display_extracted = load_words(ocr_extracted) # display the extracted text before cleaning
#         # print(f"OCR extracted text before cleaning: {display_extracted}")
#         # cleaned_extracted_text = count_word_and_char(ocr_extracted, file_type="ocr") # clean extracted text
#         # display_cleaned_extracted_text = load_words(cleaned_extracted_text) #load cleaned extracted text
#         # print(f"OCR extracted text after cleaning: {display_cleaned_extracted_text}") #display the cleaned extracted text
#         # display_extracted_char_level = load_text(cleaned_extracted_text)  #load the text for character level accuracy
#         # print(f"char level ocr text: {display_extracted_char_level}") # display cleaned extracted text for char level accuracy
#         # print("\n")
#
# #######---------------------
#         # ocr_result_displayed = load_and_clean_char(ocr_extracted)
# #######--------------------
#
#         # gt_file_path = None
#         annotation_id = None
#         # find_matching_gt_file(ocr_result_displayed)
#
#         gt_file_path = find_matching_gt_file(cleaned_extracted) #4. find gt file
#         display_gt_text = load_text(gt_file_path)
#         cleaned_gt_text = count_word_and_char(gt_file_path,file_type="gt")
#         display_cleaned_gt_text = load_text(cleaned_gt_text)
#         print(f"gt text before cleaning: {display_gt_text}")
#         print(f"gt text after cleaning: {display_cleaned_gt_text}")
#         # display_gt_text = load_words(gt_file_path)
#         # print(f"gt_text before cleaning: {display_gt_text}")
#         # cleaned_gt_text = count_word_and_char(gt_file_path, file_type="gt")
#         # display_cleaned_gt_text = load_words(cleaned_gt_text)
#         # print(f"gt_text after cleaning: {display_cleaned_gt_text}")
#         # display_gt_char_level = load_text(cleaned_gt_text)
#         # print(f"char level text: {display_gt_char_level}")
#         char_level_edit_dist = Levenshtein.distance(display_cleaned_gt_text, load_cleaned_extracted)
#         # calculate Levensthein distance
#         # word_level_edit_distance = Levenshtein.distance(display_cleaned_extracted_text,display_cleaned_gt_text) # word level accuracy
#         # print(f"word level edit distance between extracted and gt {ocr_img_id, annotation_id}: {word_level_edit_distance}")
#         print(f"char level edit distance {char_level_edit_dist}")
#         print()
#         # lev_ratio_word_level = Levenshtein.ratio(display_cleaned_extracted_text,display_cleaned_gt_text)
#         lev_ratio_char_level = Levenshtein.ratio(display_cleaned_gt_text, load_cleaned_extracted)
#         # print(f"Levenshtein ratio: {lev_ratio_word_level}")
#         print(f"Levenshtein ratio: {lev_ratio_char_level}")

def process_cropped_img():
    # 1. save cropped image
    cropped_img_path = save_cropped_img()
    print(f"Saved cropped image to {cropped_img_path}.")
    if cropped_img_path is None:
        return
    # 2. perform OCR
    ocr_extracted = perform_ocr_on_single_image(cropped_img_path)
    if ocr_extracted is None:
        print("OCR failed or returned no output.")
        return
    # 3. load extracted text before cleaning
    print(f"OCR performed on: {ocr_extracted}")
    extracted_before = load_text(ocr_extracted) #as string
    extracted_before_w =load_words(ocr_extracted) #as words
    # 4. clean extracted text
    cleaned_extracted_path = count_word_and_char(ocr_extracted, file_type="ocr")
    # 5. load cleaned extracted text
    extracted_after = load_text(cleaned_extracted_path) #use this for char level
    extracted_norm = normalize_for_char_metric(extracted_after)
    extracted_after_w = load_words(cleaned_extracted_path) #use this for char level comparison
    print(f"Extracted before cleaning: {extracted_before}")
    print(f"Extracted after cleaning: {extracted_after}")
    print(f"Extracted before cleaning (words): {extracted_before_w}")
    print(f"Extracted after cleaning(Words): {extracted_after_w}")
    # 6. find matching GT file
    gt_file_path = find_matching_gt_file(cleaned_extracted_path)
    if gt_file_path is None:
        print("No matching GT file found.")
        return
    # 7. load GT text before cleaning
    gt_before = load_text(gt_file_path) # gt char level
    gt_before_w = load_words(gt_file_path) # gt word level
    # 8. clean GT text
    cleaned_gt_path = count_word_and_char(gt_file_path, file_type="gt")
    # 9. load cleaned GT text
    gt_after = load_text(cleaned_gt_path)
    gt_norm = normalize_for_char_metric(gt_after)
    gt_after_w = load_words(cleaned_gt_path)
    print(f"GT text before cleaning: {gt_before}")
    print(f"GT text after cleaning: {gt_after}")
    print(f"GT text before cleaning (words): {gt_before_w}")
    print(f"GT text after cleaning (words): {gt_after_w}")
    # 10. calculate edit distance & ratio
    char_edit_dist = Levenshtein.distance(gt_after, extracted_after)
    char_edit_dist_2 = Levenshtein.distance(gt_norm, extracted_norm)
    print(f"Char edit distance: {char_edit_dist}")
    print(f"Char edit distance 2: {char_edit_dist_2}")
    char_ratio = Levenshtein.ratio(gt_after, extracted_after)
    char_ratio_2 = Levenshtein.ratio(gt_norm, extracted_norm)
    print(f"Character-level edit distance: {char_edit_dist}")
    print(f"Levenshtein ratio: {char_ratio}")
    print(f"Levenshtein ratio: {char_ratio_2}")

    edit_dist_word = Levenshtein.distance(gt_after_w, extracted_after_w)
    ratio_word = Levenshtein.ratio(gt_after_w, extracted_after_w)

    print(f"word-level edit distance: {edit_dist_word}")
    print(f"Levenshtein ratio -word level: {ratio_word}")


def start_gui():
    gui_window.mainloop()  # displaying the window & listen for events

# ---------- CANVAS ------------
canvas = tk.Canvas(gui_window, width=width, height=height) # creating a canvas to display the image on
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", drag_rect)
canvas.bind("<ButtonRelease-1>", on_release)
select_img_btn = tk.Button(gui_window, text="Select Image", padx=10, pady=2, command=run_img_tasks)
select_img_btn.pack(pady=6)
# save_btn = tk.Button(gui_window, text="Save Crop", command=save_cropped_img)
save_btn = tk.Button(gui_window, text="Save Crop", padx=10, pady=2, command=process_cropped_img)
save_btn.pack()
canvas.pack()
