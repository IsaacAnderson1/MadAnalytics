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


import os
os.environ["GOOGLE_CLOUD_PROJECT"]="trade-promotion-analytics"
os.environ["GOOGLE_CLOUD_LOCATION"]="us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"]="True"

from google import genai
from google.genai.types import HttpOptions
import prompt_utils
import json

client = genai.Client(http_options=HttpOptions(api_version="v1"))

all_responses = []
for prompt in prompt_utils.get_preliminary_prompts():
    response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config={
                'response_mime_type': 'application/json',
        },
    )
    try:
        parsed = json.loads(response.text)
        all_responses.append(parsed)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON for preliminary output")
with open("preliminary_outputs.json", "w", encoding="utf-8") as f:
    json.dump(all_responses, f, indent=2)
print("📁 All responses saved to preliminary_outputs.json")

all_responses = []
for prompt in prompt_utils.get_conditional_prompts():
    response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config={
                'response_mime_type': 'application/json',
        },
    )
    try:
        parsed = json.loads(response.text)
        all_responses.append(parsed)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON for conditional output")
with open("conditional_outputs.json", "w", encoding="utf-8") as f:
    json.dump(all_responses, f, indent=2)
print("📁 All responses saved to conditional_outputs.json")

i = 1
prompt = prompt_utils.intermediate_generalize_prompt
response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config={
                'response_mime_type': 'application/json',
        },
    )
try:
    parsed = json.loads(response.text)
    with open(f"final_weight{i}.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)
    print(f"📁 All responses saved to final_weight{i}.json")
except json.JSONDecodeError:
    print(f"❌ Failed to parse JSON for final weight aggregation")

prompt = prompt_utils.final_generalize_prompt
response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=prompt,
        config={
                'response_mime_type': 'application/json',
        },
    )
try:
    parsed = json.loads(response.text)
    with open(f"final_weight.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)
    print(f"📁 All responses saved to final_weight.json")
except json.JSONDecodeError:
    print(f"❌ Failed to parse JSON for final weight aggregation")