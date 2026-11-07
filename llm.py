import json
import requests 

def prompt_llm(system_prompt: str, user_prompt: str) -> dict:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen3",
        "messages": [
            #system pr0mpt injects in header
            {"role": "system", "content": system_prompt},
            #user_pr0mpt reads similar to human entry
            {"role": "user", "content": user_prompt}
        ],
        "format": "json",
        "stream": False
    }
    try:
        # Added timeout=60 so it doesn't hang forever if Ollama is unresponsive
        response = requests.post(url, json=payload, timeout=60).json()
        return json.loads(response["message"]["content"])
    except requests.exceptions.ConnectionError:
        print("\n ERROR: Could not connect to Ollama. Make sure Ollama is running ('ollama serve')!")
        raise
    except Exception as e:
        print(f"\n ERROR parsing LLM response: {e}")
        return {"public_message": "Error processing task.", "private_memory": "Failed step."}