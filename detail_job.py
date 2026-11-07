import json
import ollama


def get_agent_job_summaries(task: str) -> list[dict]:
    """Queries Ollama for a task decomposition and returns structured job data."""
    prompt = f"""Decompose the following high-level task into 3 to 6 distinct agent job assignments: '{task}'.

Return ONLY a valid JSON object formatted as follows:
{{
  "jobs": [
    {{
      "title": "Job Title",
      "summary": "1 to 2 sentence summary of what this agent does."
    }}
  ]
}}
Ensure the count of jobs is strictly between 3 and 6."""

    # Use Ollama's native JSON format mode to ensure structured parsing
    response = ollama.chat(
        model="llama3.2",  # Replace with your local model
        messages=[
            {
                "role": "system",
                "content": "You are an AI system architect. Output strictly valid JSON matching the requested schema.",
            },
            {"role": "user", "content": prompt},
        ],
        format="json",
    )

    try:
        data = json.loads(response["message"]["content"])
        return data.get("jobs", [])
    except json.JSONDecodeError:
        print("Failed to parse JSON response from Ollama.")
        return []