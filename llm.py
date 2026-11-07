import json
from openai import OpenAI

# Custom API endpoint setup
BASE_URL = "http://127.0.0.1:31415/v1"
API_KEY = "freellmapi-74d80b543e7a6340ca943283a04115b679bc6e5826414be7"
MODEL_NAME = "auto"  # Automatically routes to active models (e.g., gemini-2.5-flash)

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


def clean_json_response(content: str) -> str:
    """Strips markdown formatting if the proxy wraps JSON in triple backticks."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def prompt_llm(system_prompt: str, user_prompt: str) -> dict:
    """Queries the proxy LLM endpoint for a JSON structured response."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        raw_content = response.choices[0].message.content
        cleaned_content = clean_json_response(raw_content)
        return json.loads(cleaned_content)

    except Exception as e:
        print(f"\n ERROR parsing LLM response: {e}")
        return {
            "public_message": "Error processing task.",
            "private_memory": "Failed step.",
        }