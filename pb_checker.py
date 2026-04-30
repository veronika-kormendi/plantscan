import csv
import text_utils as txt
from config_refactor import EXCLUDE_WORDS_PATH

def make_cvs_to_dict(csv_filepath):
    categories = {}
    with open(csv_filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for col in reader.fieldnames:
            categories[col] = [] #create list
        for row in reader:
            for col in reader.fieldnames:
                value = row[col].strip()
                if value:
                    categories[col].append(value)
    return categories

# result = make_cvs_to_dict(EXCLUDE_WORDS_PATH)
# print(result.keys(), result.values())
# for key, value in result.items(): #checking the content
#     print(key, value)
def load_dictionary(dictionary):
    # print("dictionary")
    for key, value in dictionary.items():  # checking the content
        print(key, value)

# load_dictionary(result)


# def is_it_plant_based(input_file_path, exclude_words_path):
#     """this function takes a txt file and checks
#     if any words from the exclude list matches with the currently examined word
#     if there is a match: False -not plant based
#     if there is a match: True - plant based"""
#     words_to_check = txt.load_words(input_file_path)
#     print(f"words_to_check: {words_to_check}")
#     # for word in words_to_check:
#     #get dictionary of exclude words
#     exclude_words_dict = make_cvs_to_dict(EXCLUDE_WORDS_PATH)
#     #go through the dict words and check is it the same as the word in the list to check
#     for word in words_to_check:
#         for key, value in exclude_words_dict.items():
#             if value == word in words_to_check: # match
#                 print(f"product is not plant-based, it contains {value}")
#             else:
#                 print(f"product is plant-based)")
def is_it_plant_based(input_file_path, exclude_words_path):
    words_to_check = txt.load_words(input_file_path) #get words from file to check
    exclude_words_dict = make_cvs_to_dict(exclude_words_path) # get the exclude list, make it into a dictionary
    exclude_words = set() # flatten all excluded words into one set
    for values in exclude_words_dict.values(): # go through the word in dict
        exclude_words.update(values) #add them to the set
    for word in words_to_check: # check for match
        if word in exclude_words:
            print(f"Product is NOT plant-based (contains: {word})")
            return False  # stop immediately

    print("Product is plant-based")   # if no matches found
    return True

# is_it_plant_based('C:\\Users\\veron\\PycharmProjects\\plantscan\\cleaned_folder_single\\IMG_7476_cropped_cleaned_ocr.txt', EXCLUDE_WORDS_PATH) #test
# is_it_plant_based('C:\\Users\\veron\\PycharmProjects\\plantscan\\cleaned_folder_single\\IMG_8579_cropped_cleaned_ocr.txt', EXCLUDE_WORDS_PATH) #test
