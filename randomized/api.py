import os
os.environ["GOOGLE_CLOUD_PROJECT"]="trade-promotion-analytics"
os.environ["GOOGLE_CLOUD_LOCATION"]="us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"]="True"

from google import genai
from google.genai.types import HttpOptions

prompt = "Testing"

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model="gemini-2.5-pro-exp-03-25",
    contents=prompt,
    config={
            'response_mime_type': 'application/json',
    },
)
print(response.text)

import json

def format_gemini_prompt(weight_sets: list, user_input: dict) -> str:
    prompt_template = """""".strip()

    return prompt_template.format(
        weight_sets_json=json.dumps(weight_sets, indent=2),
        user_input_json=json.dumps(user_input, indent=2)
    )