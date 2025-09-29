import pandas as pd

# Replace 'your_file.csv' with the actual path to your CSV file
file_path = 'data.csv'

# Load the CSV into a pandas DataFrame
try:
    df = pd.read_csv(file_path)
    print("CSV loaded successfully. Here are the first few rows:")
    print(df.head())
except FileNotFoundError:
    print(f"File not found: {file_path}")
except pd.errors.ParserError:
    print("There was a parsing error while reading the CSV.")
except Exception as e:
    print(f"An error occurred: {e}")