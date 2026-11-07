import json
from agent import Agent
from openai import OpenAI

# Custom API endpoint details
BASE_URL = "http://127.0.0.1:31415/v1"
API_KEY = "freellmapi-74d80b543e7a6340ca943283a04115b679bc6e5826414be7"

# Using 'auto' allows the proxy router to automatically select an active free model,
# or explicit available models like 'gemini-2.5-flash' / 'gemini-3.5-flash'
MODEL_NAME = "auto"

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

ORCHESTRATOR_PROMPT = """ You are a multi agent system Architect.
Given a USER TASK and a SECURITY RISK LEVEL (1-10), design a multi-agent system.

AGENT DESIGN RULES:
- Break the task into the stages a person would actually follow to complete it.
- Every agent must contribute directly to the user's task. No unrelated roles.
- Each role says: what it receives, what it does, and what it passes on.
- The flow of "passes on to" in the roles must match the adjacency list.

NAMING RULES:
- Choose each agent's name once, then copy it EXACTLY (same spelling, same capitalization, no spaces) everywhere it appears.
- The keys of "adjacency_list" and the keys of "agent_roles" must be the SAME set of names.
- Every name inside an adjacency list must also be a key in "agent_roles".

TOPOLOGY DEFINITIONS:
- Linear: agents form one line. Each agent sends to exactly the next agent.
- Star: ONE hub agent connects to every other agent. Spokes talk ONLY to the hub.
- Complete: all agents are connected to each other.

Return ONLY a valid JSON object in exactly this format:
{
  "topology_type": "Linear" or "Complete" or "Star",
  "adjacency_list": {"<Agent>": ["<TargetAgent>", ...]},
  "reasoning": "<one or two sentences>",
  "agent_roles": {"<Agent>": "<role and instructions>"}
}
"""


def clean_json_response(content: str) -> str:
    """Strips Markdown backticks if the proxy wraps JSON in markdown code blocks."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def get_agent_job_summaries(task: str, security_score: str = "5") -> tuple:
    level = int(security_score)
    topology = (
        "Linear" if level >= 8 else "Star" if level >= 4 else "Complete"
    )

    prompt = (
        f"Design a multi-agent system for task: '{task}' "
        f"with Security Level: {level}/10. "
        f"REQUIRED TOPOLOGY: {topology}. Do not choose a different one."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw_content = response.choices[0].message.content
    cleaned_content = clean_json_response(raw_content)

    data = json.loads(cleaned_content)
    print("Orchestrator output:", json.dumps(data, indent=2))

    adjacency = data.get("adjacency_list", {})
    roles = data.get("agent_roles", {})
    names = list(adjacency.keys())

    if data.get("topology_type") == "Star":
        entry = max(adjacency, key=lambda a: len(adjacency[a]))
        output = entry
    else:
        entry = names[0]
        output = names[-1]

    spec = {
        "adjacency": adjacency,
        "entry_agent": entry,
        "output_agent": output,
    }

    agents = {
        name: Agent(name, desc, task, adjacency.get(name, []))
        for name, desc in roles.items()
    }

    return spec, agents, task