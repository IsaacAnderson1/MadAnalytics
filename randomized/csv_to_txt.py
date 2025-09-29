import csv
import sys


def csv_to_txt(csv_file_path: str, txt_file_path: str, delimiter: str = "\t") -> None:
    """
    Reads a CSV file and writes its contents to a text file with a specified delimiter.

    :param csv_file_path: The path to the input CSV file.
    :param txt_file_path: The path to the output text file.
    :param delimiter: The delimiter to use in the output text (default is tab).
    """
    try:
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csv_file, \
                open(txt_file_path, mode="w", newline="", encoding="utf-8") as txt_file:

            reader = csv.reader(csv_file)
            for row in reader:
                # Join each row's columns with the specified delimiter
                line = delimiter.join(row)
                txt_file.write(line + "\n")

        print(f"Successfully converted '{csv_file_path}' to '{txt_file_path}'.")
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

csv_to_txt("data.csv", "data.txt", "\t")