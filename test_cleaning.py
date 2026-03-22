import os, unicodedata, string

my_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\output"
annot_folder = "C:\\Users\\veron\\PycharmProjects\\plantscan\\annotation"

cleaned_path = "C:\\Users\\veron\\PycharmProjects\\plantscan\\output\\cleaned_text"

def clean_line(line):
    line = line.strip()
    line = line.lower()
    line = unicodedata.normalize("NFKC", line)
    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
    line = line.translate(translator)
    # remove numbers
    empty_string = ""
    for char in line:
        if not char.isdigit():
            empty_string += char
    line = empty_string
    return line

def save_cleaned_files(folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(folder):
        if not file.endswith(".txt"):
            continue

        input_path = os.path.join(folder, file)
        output_path = os.path.join(output_folder, file)

        cleaned_lines = []

        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                cleaned = clean_line(line)
                cleaned_lines.append(cleaned)

        # write cleaned text
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("\n".join(cleaned_lines))

        print(f"Saved cleaned file: {output_path}")

save_cleaned_files(my_folder, cleaned_path)