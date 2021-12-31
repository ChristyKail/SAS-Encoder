import csv
import os


def load_csv(file_name):

    if not os.path.isfile(file_name):

        return None

    with open(file_name) as file_handler:

        file_reader = csv.reader(file_handler)
        dictionary = {rows[0]: rows[1] for rows in file_reader if rows[0]}

    return dictionary
