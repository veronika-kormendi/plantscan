import tkinter as tk # for GUI
import ttkbootstrap as ttk # for modern GUI
from config import *
import os
from PIL import Image, ImageTk  # for managing images
from utils import (select_img_from, heic_to_jpg, colour_to_greyscale, resize_image, make_tk_img, \
                   perform_ocr_on_single_image, load_words, load_text, count_word_and_char, normalize_for_char_metric,
                   find_matching_gt_file, calculate_wer_manual, calculate_wac, calculate_cac, calculate_cer_manual, evaluate_preprocessed,
                   each_word_on_new_line, postprocess_text)
import Levenshtein
from jiwer import wer

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

def process_cropped_img():
    # ---------------------------------------------------------
    # 0. Save cropped image + run OCR
    # ---------------------------------------------------------
    cropped_img_path = save_cropped_img()
    print(f"Saved cropped image to {cropped_img_path}.")
    if not cropped_img_path:
        return
    ocr_extracted = perform_ocr_on_single_image(cropped_img_path)
    if not ocr_extracted:
        print("OCR failed or returned no output.")
        return
    print(f"OCR performed on: {ocr_extracted}")
    # ---------------------------------------------------------
    # 1. LOAD & PRINT OCR + GT BEFORE CLEANING
    # ---------------------------------------------------------
    extracted_before = load_text(ocr_extracted)
    extracted_before_w = load_words(ocr_extracted)
    print("\n--- EXTRACTED TEXT BEFORE CLEANING ---")
    print(extracted_before)
    print(extracted_before_w)

    # Find matching GT file (before cleaning)
    gt_file_path = find_matching_gt_file(ocr_extracted)
    if not gt_file_path:
        print("No matching GT file found.")
        return

    gt_before = load_text(gt_file_path)
    gt_before_w = load_words(gt_file_path)

    print("\n--- GT TEXT BEFORE CLEANING ---")
    print(gt_before)
    print("GT words:", gt_before_w)

    # ---------------------------------------------------------
    # 2. CLEAN OCR + GT TEXT
    # ---------------------------------------------------------
    cleaned_extracted_path = count_word_and_char(ocr_extracted, file_type="ocr")
    cleaned_gt_path = count_word_and_char(gt_file_path, file_type="gt")

    # ---------------------------------------------------------
    # 3. LOAD & DISPLAY CLEANED OCR + GT
    # ---------------------------------------------------------
    extracted_after = load_text(cleaned_extracted_path)
    extracted_after_w = load_words(cleaned_extracted_path)
    extracted_norm = normalize_for_char_metric(extracted_after)

    gt_after = load_text(cleaned_gt_path) #char level
    gt_after_w = load_words(cleaned_gt_path) #word level
    gt_norm = normalize_for_char_metric(gt_after)

    print("\n--- EXTRACTED TEXT AFTER CLEANING ---")
    print(extracted_after)
    print("OCR extracted words:", extracted_after_w)

    print("\n--- GT TEXT AFTER CLEANING ---")
    print(gt_after)
    print("GT words:", gt_after_w)

    # ---------------------------------------------------------
    # 4. CALCULATE LEVENSHTEIN DISTANCES & RATIOS
    # ---------------------------------------------------------
    print("\n--- METRICS ---")

    # Character-level
    char_edit_dist = Levenshtein.distance(gt_after, extracted_after)
    char_edit_dist_norm = Levenshtein.distance(gt_norm, extracted_norm)
    char_ratio = Levenshtein.ratio(gt_after, extracted_after)
    char_ratio_norm = Levenshtein.ratio(gt_norm, extracted_norm)

    print(f"Char edit distance: {char_edit_dist}")
    print(f"Char edit distance (normalized): {char_edit_dist_norm}")
    print(f"Char ratio: {char_ratio}")
    print(f"Char ratio (normalized): {char_ratio_norm}")

    # Word-level
    word_edit_dist = Levenshtein.distance(gt_after_w, extracted_after_w)
    word_ratio = Levenshtein.ratio(gt_after_w, extracted_after_w)

    print(f"Word edit distance: {word_edit_dist}")
    print(f"Word ratio: {word_ratio}")

    # calculate WER
    gt_word_count = len(gt_after_w)
    wer_manual = calculate_wer_manual(word_edit_dist, gt_word_count)
    print(f"WER (manual): {wer_manual}")
    # calculate CER
    cer = calculate_cer_manual(char_edit_dist_norm, gt_norm)
    print(f"CER (manual): {cer}")

    # --------- word & char accuracy calculations
    wac = calculate_wac(wer_manual)
    wac_rounded = round(wac, 2)*100
    print(f"WAC: {wac}, rounded: {wac_rounded}%")
    cac = calculate_cac(cer)
    cac_rounded = round(cac, 2)*100
    print(f"CAC: {cac}, rounded: {cac_rounded}%")

words_per_line_folder_path = each_word_on_new_line(CLEANED_FOLDER_PATH, CLEANED_2)
# postprocess_text(words_per_line_folder_path, POSTPROCESS_OUT_FOLDER)
# postprocess_text(words_per_line_folder_path, CANDIDATE_WORDS_PATH) # for saving candidate words to csv


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

eval_btn = tk.Button(gui_window, text="Evaluate Preprocessed", padx=10, pady=2,
                     command=lambda: evaluate_preprocessed(CLEANED_FOLDER_PATH, "preprocessed_metrics.csv"))
eval_btn.pack(pady=6)

eval_btn = tk.Button(gui_window, text="postprocess", padx=10, pady=2,
                     command=lambda: postprocess_text(CLEANED_FOLDER_PATH, "preprocessed_metrics.csv"))
eval_btn.pack(pady=6)


eval_btn = tk.Button(gui_window, text="Evaluate Postprocessed", padx=10, pady=2,
                     command=lambda: evaluate_preprocessed(words_per_line_folder_path, "postprocessed_metrics.csv"))
eval_btn.pack(pady=6)
canvas.pack()
