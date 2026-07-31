import os


def find_file(filename, search_path="."):

    for root, dirs, files in os.walk(search_path):

        for file in files:

            if filename.lower() in file.lower():

                return os.path.join(root, file)

    return "File not found."