import os # for file handling
import Levenshtein
from config_refactor import CLEANED_FOLDER_PATH
import csv
import pandas as pd
from text_utils import get_img_id, load_text, load_words, normalize_for_char_metric

def calculate_wer_manual(word_edit_distance, gt_word_count):
    """
    Calculate Word Error Rate (WER) using edit distance and GT word count.
    :param word_edit_distance: Levenshtein distance between GT words and OCR words
    :param gt_word_count: number of words in the GT text
    :return: WER value (float)
    """
    if gt_word_count == 0:
        return 0.0  # no GT words → no errors possible

    wer_value = word_edit_distance / gt_word_count
    return wer_value

def calculate_cer_manual(char_edit_dist_norm, gt_norm):
    n = len(gt_norm) #total number of characters
    if n == 0:
        return 0.0
    cer_value = char_edit_dist_norm / n
    return cer_value

def calculate_cac(cer_value):
    #calculate character accuracy
    cac = 1 - cer_value
    return cac

def calculate_wac(wer_value):
    wac = 1 - wer_value
    return wac

def evaluate_preprocessed(ocr_path, folder_path, output_csv="preprocessed_metrics.csv"):
    """ compare ocr text with gt text
    this function is to evaluate the cleaned ocr extracted text by comparing the content of the text file with the cleand gt text file's contents
    :param ocr_path: full filepath to ocr extracted text file
    :param folder_path: folder path of cleaned ocr extracted text file and cleaned gt text file
    :param output_csv: path where to save the csv file with the metrics results"""
    results = []
    input_txt_file = os.path.basename(ocr_path) # IMG_7476_cropped_cleaned_ocr.txt
    # Derive base id, e.g. IMG_9163 from IMG_9163_cropped_cleaned_ocr.txt
    img_id = get_img_id(input_txt_file)
    # Find matching cleaned GT file in the same folder
    # e.g. IMG_9163_annotation_cleaned_gt.txt
    gt_path = None
    for f in os.listdir(folder_path):
            if f.endswith("_cleaned_gt.txt") and get_img_id(f) == img_id:
                gt_path = os.path.join(folder_path, f)
                break

    if not gt_path:
        print(f"No cleaned GT found for {input_txt_file}.")
        return None

    # --- Load OCR cleaned text ---
    ocr_text = load_text(ocr_path)
    ocr_norm = normalize_for_char_metric(ocr_text)
    ocr_words = load_words(ocr_path)

    # --- Load GT cleaned text ---
    gt_text = load_text(gt_path)
    gt_norm = normalize_for_char_metric(gt_text)
    gt_words = load_words(gt_path)

    # --- Character-level metrics
    char_edit = Levenshtein.distance(gt_text, ocr_text)
    char_edit_norm = Levenshtein.distance(gt_norm, ocr_norm)
    char_ratio = Levenshtein.ratio(gt_text, ocr_text)
    char_ratio_norm = Levenshtein.ratio(gt_norm, ocr_norm)

    cer = calculate_cer_manual(char_edit_norm, gt_norm)
    cac = calculate_cac(cer)

    # --- Word-level metrics ---
    word_edit = Levenshtein.distance(gt_words, ocr_words)
    gt_word_count = len(gt_words)
    wer = calculate_wer_manual(word_edit, gt_word_count)
    wac = calculate_wac(wer)

    # print("\n--- DEBUG OCR TEXT USED BY EVALUATOR ---")
    # print(ocr_text)
    # print("\n--- DEBUG GT TEXT USED BY EVALUATOR ---")
    # print(gt_text)

    results.append({
        "image": img_id,
        "char_edit": char_edit,
        "char_edit_norm": char_edit_norm,
        "char_ratio": char_ratio,
        "char_ratio_norm": char_ratio_norm,
        "cer": cer,
        "cac": cac,
        "word_edit": word_edit,
        "word_ratio": Levenshtein.ratio(gt_words, ocr_words),
        "wer": wer,
        "wac": wac,
    })

    # Save CSV
    if results:
        keys = results[0].keys()
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"Metrics saved to {output_csv}")
    return results

#=--------------------
def evaluate_postprocessed(text_path_of_postprocessed, output_csv="postprocessed_metrics.csv"):
    """this function is to evaluate postprocessed text
    :param text_path_of_postprocessed: full filepath to postprocessed text file
    :param folder_path: folder path of gt text
    :param output_csv: path where to save the csv file with the metrics results"""
    results = []
    input_txt_file = os.path.basename(text_path_of_postprocessed) # IMG_7476_postprocessed.txt
    # Derive base id, e.g. IMG_9163 from IMG_9163_cropped_cleaned_ocr.txt
    img_id = get_img_id(input_txt_file)
    # Find matching cleaned GT file in the same folder
    # e.g. IMG_7476_annotation_cleaned_gt.txt
    gt_path = None
    for f in os.listdir(CLEANED_FOLDER_PATH): #check for gt text in cleaned folder
        if f.endswith("_cleaned_gt.txt") and get_img_id(f) == img_id:
            gt_path = os.path.join(CLEANED_FOLDER_PATH, f)
            break

    if not gt_path:
        print(f"No cleaned GT found for {input_txt_file}.")
        return None

    # --- load postprocessed text ---
    postprocessed_text = load_text(text_path_of_postprocessed)
    postprocessed_norm = normalize_for_char_metric(postprocessed_text)
    postprocessed_words = load_words(text_path_of_postprocessed)

    # --- Load GT cleaned text ---
    gt_text = load_text(gt_path)
    gt_norm = normalize_for_char_metric(gt_text)
    gt_words = load_words(gt_path)

    # --- Character-level metrics
    char_edit = Levenshtein.distance(gt_text, postprocessed_text)
    char_edit_norm = Levenshtein.distance(gt_norm, postprocessed_norm)
    char_ratio = Levenshtein.ratio(gt_text, postprocessed_text)
    char_ratio_norm = Levenshtein.ratio(gt_norm, postprocessed_norm)

    cer = calculate_cer_manual(char_edit_norm, gt_norm)
    cac = calculate_cac(cer)

    # --- Word-level metrics ---
    word_edit = Levenshtein.distance(gt_words, postprocessed_words)
    gt_word_count = len(gt_words)
    wer = calculate_wer_manual(word_edit, gt_word_count)
    wac = calculate_wac(wer)

    # print("\n--- DEBUG OCR TEXT USED BY EVALUATOR ---")
    # print(ocr_text)
    #
    # print("\n--- DEBUG GT TEXT USED BY EVALUATOR ---")
    # print(gt_text)

    results.append({
        "image": img_id,
        "char_edit": char_edit,
        "char_edit_norm": char_edit_norm,
        "char_ratio": char_ratio,
        "char_ratio_norm": char_ratio_norm,
        "cer": cer,
        "cac": cac,
        "word_edit": word_edit,
        "word_ratio": Levenshtein.ratio(gt_words, postprocessed_words),
        "wer": wer,
        "wac": wac,
    })

    # Save CSV
    if results:
        keys = results[0].keys()
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"Metrics saved to {output_csv}")
    return results

def analyse_metrics(csv_in_path, csv_summary_path):
    """function for summarizing the metrics generated, takes a csv file"""
    df = pd.read_csv(csv_in_path)
    df_copy = df.copy()
    metrics_summary = df_copy.describe()
    #columns
    cer_col = df_copy["cer"]
    cac_col = df_copy["cac"]
    wer_col = df_copy["wer"]
    wac_col = df_copy["wac"]
    w_edit_col = df_copy["word_edit"]
    #benchmark
    #-------CER-----
    excellent_cer = df_copy[cer_col <= 0.02] # if cer is 2% or less
    good_cer = df_copy[(cer_col > 0.02) & (cer_col <= 0.05)] # 2-5%
    needs_review_cer = df_copy[(cer_col > 0.05) & (cer_col <= 0.1)] # 5-10% -needs review
    poor_cer = df_copy[cer_col > 0.1] #above 10%
    # -------WER----------
    excellent_wer = df_copy[wer_col <= 0.02] # 2 or less than 2 %
    good_wer = df_copy[(wer_col > 0.02) & (wer_col <= 0.1)] # 2-10%
    poor_wer = df_copy[wer_col > 0.1] #above 10%
    #-----the number of words edited in the text
    excellent_word_edit_dist = df_copy[w_edit_col <= 1] # 1 or less word edited
    good_word_edit_dist = df_copy[(w_edit_col > 1) & (w_edit_col <= 3)] #2-3 words edited
    poor_word_edit_dist = df_copy[w_edit_col > 3] # above 3
    #------COUNT---------- how many images of the dataset in each category
    excellent_cer_count = len(excellent_cer)
    good_cer_count = len(good_cer)
    needs_review_cer_count = len(needs_review_cer)
    poor_cer_count = len(poor_cer)

    excellent_wer_count = len(excellent_wer)
    good_wer_count = len(good_wer)
    poor_wer_count = len(poor_wer)

    excellent_word_edit_dist_count = len(excellent_word_edit_dist)
    good_word_edit_dist_count = len(good_word_edit_dist)
    poor_word_edit_dist_count = len(poor_word_edit_dist)
    print(f"Summary stats: \n{metrics_summary}\n")
    print(f"Excellent cer: {excellent_cer}, good cer: {good_cer}, needs review cer: {needs_review_cer}, poor cer: {poor_cer}")
    print(f"Num excellent cer: {excellent_cer_count}, good cer count: {good_cer_count}, needs review cer count: {needs_review_cer_count}, poor cer: {poor_cer_count}")
    print(f"good wer: {excellent_wer}, avg wer: {good_wer}, poor wer: {poor_wer}")
    print(f"num good wer: {excellent_wer_count}, avg wer: {good_wer_count}, num poor wer: {poor_wer_count}")
    print(f"excellent word edit dist count: {excellent_word_edit_dist_count}, good word edit dist count: {good_word_edit_dist_count},  poor word edit dist count: {poor_word_edit_dist_count}")
    analysis_dict = {
        "mean_cer": cer_col.mean(),
        "min_cer": cer_col.min(),
        "max_cer": cer_col.max(),
        "mean_wer": wer_col.mean(),
        "min_wer": wer_col.min(),
        "max_wer": wer_col.max(),
        "mean_cac": cac_col.mean(),
        "mean_wac": wac_col.mean(),
        "mean_word_edit": w_edit_col.mean(),
        "min_word_edit": w_edit_col.min(),
        "max_word_edit": w_edit_col.max(),
        # --- CER categories ---
        "excellent_cer_count": excellent_cer_count,
        "good_cer_count": good_cer_count,
        "needs_review_cer_count": needs_review_cer_count,
        "poor_cer_count": poor_cer_count,
        # --- WER categories ---
        "excellent_wer_count": excellent_wer_count,
        "good_wer_count": good_wer_count,
        "poor_wer_count": poor_wer_count,
        # --- Word edit distance categories ---
        "excellent_word_edit_dist_count": excellent_word_edit_dist_count,
        "good_word_edit_dist_count": good_word_edit_dist_count,
        "poor_word_edit_dist_count": poor_word_edit_dist_count,
        # --- Total samples ---
        "total_samples": len(df_copy)
    }
    analysis_df = pd.DataFrame.from_dict(analysis_dict, orient="index", columns=["value"])
    summary_df = df_copy.describe().T
    # summary.insert(0, "metric", summary.index)
    with open(csv_summary_path, "w", encoding="utf-8") as f:
        f.write("Summary stats: \n")
        summary_df.to_csv(f)
        f.write(f"\nanalysis stats\n")
        analysis_df.to_csv(f)
    print(f"Analysis summary saved to {csv_summary_path}")

