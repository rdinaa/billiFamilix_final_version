import os
import re

input_folder = "/Users/maximegillot/Desktop/Hackathon/BILLI - invoiceCalculation"
output_folder = "/Users/maximegillot/Desktop/Hackathon/Cleaned_BILLI"

def find_java_files(directory):
    java_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))

    return java_files


def remove_comments(java_code):
    # Remove single line comments
    java_code = re.sub(re.compile("//.*?\n"), "", java_code)

    # Remove multiline comments
    java_code = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", java_code)

    return java_code



def remove_all_java_files_comments(input_folder, output_folder):

    java_files = find_java_files(input_folder)

    for input_file in java_files:
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(input_file, 'r', encoding='latin-1', errors='strict') as file:
                content = file.read()


        print('cleaning :', input_file)
        cleaned_java_code = remove_comments(content)

        write_path = output_folder + "/" + os.path.basename(input_file)

        with open(write_path, 'w') as output_file:
            output_file.write(cleaned_java_code)


remove_all_java_files_comments(input_folder,output_folder)