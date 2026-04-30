import os # for file handling
from spellchecker import SpellChecker # for postprocessing
import csv
spell = SpellChecker() # load default word frequency list
extra_words = ["flavouring", "sucralose", "colours", "sorbate", "sugar", "caramelised", "flavour", "guar", "thermophilus",
               "bulgaricus", "lecithins", "folic", "fibre", "sucralose", "stabiliser", "stabilisers", "curcumin",
               "xanthan", "sundried", "crouton", "croutons", "colour", "humectants", "acerola", "pasteurised", "coagulans", "flavourings"]
# add extra words to spell checker dictionary
for word in extra_words:
    spell.word_frequency.add(word)

#-----------
def postprocess_text(ocr_filepath, output_folder_path):
    """Postprocess a single cleaned OCR text file, preserve line structure,
    correct misspellings, and write a candidates CSV."""

    os.makedirs(output_folder_path, exist_ok=True)

    # CSV path (one shared CSV for all processed files)
    candidates_csv_path = os.path.join(output_folder_path, "candidates_updated_dict_single.csv")
    csv_exists = os.path.exists(candidates_csv_path)

    # Open CSV in append mode so multiple files can be processed
    csvfile = open(candidates_csv_path, "a", newline="", encoding="utf-8")
    writer = csv.writer(csvfile)

    # Write header only once
    if not csv_exists:
        writer.writerow(["filename", "misspelt_word", "candidates"])

    filename = os.path.basename(ocr_filepath)

    # Read file preserving lines
    with open(ocr_filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"\nFile: {filename}")

    corrected_lines = []
    all_misspelt = set()

    for line in lines:
        stripped_line = line.strip()

        if not stripped_line:
            corrected_lines.append("")
            continue

        words = stripped_line.split()
        misspelt = spell.unknown(words)
        all_misspelt.update(misspelt)

        # Write misspellings + candidates to CSV
        for w in misspelt:
            candidates = spell.candidates(w)
            candidates_str = ",".join(candidates) if candidates else ""
            writer.writerow([filename, w, candidates_str])

        # Correct words
        corrected_words = []
        for w in words:
            if w in misspelt:
                corrected = spell.correction(w) or w
                corrected_words.append(corrected)
            else:
                corrected_words.append(w)

        corrected_lines.append(" ".join(corrected_words))

    csvfile.close()

    print(f"Found {len(all_misspelt)} misspelled words")
    print(f"misspelt: {all_misspelt}")

    # Build output filename
    base = filename.replace("_cropped_cleaned_ocr.txt", "")
    new_filename = f"{base}_postprocessed.txt"
    out_path = os.path.join(output_folder_path, new_filename)

    # Save corrected file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(corrected_lines))

    print(f"Saved corrected file to: {out_path}")

    return out_path
#---------


# def postprocess_text(ocr_filepath, output_folder_path):
#     """Postprocess a single, cleaned OCR text file while preserving line structure."""
#     os.makedirs(output_folder_path, exist_ok=True)
#     filename = os.path.basename(ocr_filepath) #
#     # Read file as lines so the original structure is preserved
#     with open(ocr_filepath, "r", encoding="utf-8") as f:
#         lines = f.readlines()
#     print(f"\nFile: {filename}")
#     corrected_lines = []
#     all_misspelt = set()
#     for line in lines:
#         stripped_line = line.strip()
#         # Preserve blank lines
#         if not stripped_line:
#             corrected_lines.append("")
#             continue
#         words = stripped_line.split()
#         misspelt = spell.unknown(words)
#         all_misspelt.update(misspelt)
#         corrected_words = []
#         for w in words:
#             if w in misspelt:
#                 corrected = spell.correction(w)
#                 if corrected is None:
#                     corrected = w
#                 corrected_words.append(corrected)
#             else:
#                 corrected_words.append(w)
#         # Rebuild the line in the same line-based structure
#         corrected_line = " ".join(corrected_words)
#         corrected_lines.append(corrected_line)
#     print(f"Found {len(all_misspelt)} misspelled words")
#     print(f"misspelt: {all_misspelt}")
#     base = filename.replace("_cropped_cleaned_ocr.txt", "")
#     new_filename = f"{base}_postprocessed.txt"
#     out_path = os.path.join(output_folder_path, new_filename)
#     # Save with the same line structure as the input OCR text
#     with open(out_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(corrected_lines))
#     print(f"Saved corrected file to: {out_path}")
#
#     return out_path

# def postprocess_text(input_folder_path, output_folder_path):
#     """Postprocess multiple cleaned OCR text files while preserving line structure."""
#     os.makedirs(output_folder_path, exist_ok=True)
#     for filename in os.listdir(input_folder_path):
#         if not filename.endswith("_cleaned_ocr.txt"):
#             continue
#         input_path = os.path.join(input_folder_path, filename)
#         # Read file as lines so the original structure is preserved
#         with open(input_path, "r", encoding="utf-8") as f:
#             lines = f.readlines()
#         print(f"\nFile: {filename}")
#         corrected_lines = []
#         all_misspelt = set()
#         for line in lines:
#             stripped_line = line.strip()
#             # Preserve blank lines
#             if not stripped_line:
#                 corrected_lines.append("")
#                 continue
#             words = stripped_line.split()
#             misspelt = spell.unknown(words)
#             all_misspelt.update(misspelt)
#             corrected_words = []
#             for w in words:
#                 if w in misspelt:
#                     corrected = spell.correction(w)
#                     if corrected is None:
#                         corrected = w
#                     corrected_words.append(corrected)
#                 else:
#                     corrected_words.append(w)
#             # Rebuild the line in the same line-based structure
#             corrected_line = " ".join(corrected_words)
#             corrected_lines.append(corrected_line)
#         print(f"Found {len(all_misspelt)} misspelled words")
#         print(f"misspelt: {all_misspelt}")
#         base = filename.replace("_cropped_cleaned_ocr.txt", "")
#         new_filename = f"{base}_postprocessed.txt"
#         out_path = os.path.join(output_folder_path, new_filename)
#         # Save with the same line structure as the input OCR text
#         with open(out_path, "w", encoding="utf-8") as f:
#             f.write("\n".join(corrected_lines))
#         print(f"Saved corrected file to: {out_path}")
#
#     return output_folder_path