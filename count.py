def count_word_and_char(text_file, file_type="ocr"):
    """
    Cleans the text, counts the number of words and chars in a text file.
    :param text_file:
    :return: cleaned text
    """
    word_count = 0
    char_count = 0
    cleaned_lines =[]
    if not os.path.exists(cleaned_folder_path):
        os.makedirs(cleaned_folder_path)
    origin = os.path.basename(text_file)
    without_extension = os.path.splitext(origin)[0]
    cleaned_filename = f"{without_extension}_cleaned_super.txt"
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
