import json
from google import genai
from google.genai import types

client = genai.Client()   # reads GEMINI_API_KEY from the environment

def prompt_hosted(system_prompt: str, user_prompt: str) -> dict:
    response = client.models.generate_content(
        model="gemini-3.8-flash",      # check AI Studio for the current name
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    return json.loads(response.text)