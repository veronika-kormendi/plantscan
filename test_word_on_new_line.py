import os

my_input_folder = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\cleaned_folder'
my_output_folder = 'C:\\Users\\veron\\PycharmProjects\\plantscan\\word_per_line'


def each_word_on_new_line(input_folder_path, output_folder_path):
    os.makedirs(output_folder_path, exist_ok=True) # create output folder
    for filename in os.listdir(input_folder_path):
        in_path = os.path.join(input_folder_path, filename)
        with open(in_path, "r", encoding="utf-8") as f:
            text = f.read()
        words = text.split()
        cleaned = [w.strip() for w in words if w.strip()]
        out_path = os.path.join(output_folder_path, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            for word in cleaned:
                f.write(word + "\n")

    return output_folder_path


each_word_on_new_line(my_input_folder, my_output_folder)