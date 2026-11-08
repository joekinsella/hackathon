import json
import os
import time
from openai import OpenAI

# Reads key from GEMINI_API_KEY or OPENAI_API_KEY environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "No API key set! Run 'set OPENAI_API_KEY=your_key' in terminal before running."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

CHEAPEST_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]


def clean_json_response(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def prompt_hosted(system_prompt: str, user_prompt: str, max_retries: int = 3) -> dict:
    for model_name in CHEAPEST_MODELS:
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🚀 [OPENAI LLM] Querying {model_name}...")
                response = client.chat.completions.create(
                    model=model_name,
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
                err_msg = str(e)
                if "429" in err_msg or "insufficient_quota" in err_msg:
                    print(
                        f"⚠️ [OPENAI LLM] Quota/rate limit hit on {model_name}."
                    )
                    break
                elif attempt < max_retries:
                    wait_seconds = attempt * 2
                    print(
                        f"⚠️ [OPENAI LLM] Error on {model_name}: {err_msg}. Retrying in {wait_seconds}s..."
                    )
                    time.sleep(wait_seconds)

    raise RuntimeError("All configured OpenAI models failed to return a response.")