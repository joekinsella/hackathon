import json
import ollama


def get_agent_job_summaries(
    task: str, security_allowance: str = "5"
) -> dict:
    """Queries Ollama for a task decomposition and returns structured job data based on task and security level."""
    prompt = f"Design a multi-agent system for task: '{task}' with Security Level: {security_allowance}/10."

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": """You are a Multi-Agent System Architect.
Given a USER TASK and a SECURITY RISK LEVEL (1-10), design a multi-agent system.

STEP 1: Choose a topology based strictly on security requirements:
- "Linear": Highest Security (8-10). Strict sequence of isolated stages to minimize attack surface and data leaks.
- "Star": Medium Security (4-7). A central coordinator delegates to isolated specialists and inspects messages.
- "Complete": Lowest Security (1-3). Fully interconnected mesh allowing unrestricted communication among all agents.

STEP 2: Define the agents.
Use 3 to 6 agents with descriptive names to quickly identify their roles and responsibilities.
Note, the agents must have actual names based on jobs, not just "agent 1, agent 2...", do not include the word agent in the name

TOPOLOGY RULES:

Linear: agents form one line. Each agent sends to exactly the next agent.
The last agent has []. No agent has more than one target. No replies backward.

Star: ONE hub agent connects to every other agent. Spokes talk ONLY to the hub,
never to each other. The hub lists all spokes; each spoke lists only the hub.

Complete: all agents are connected to each other. Each agent lists all other agents as its targets.

The examples above only show the SHAPE. Use your own agent names that fit the task.

STEP 3: Write a role description for each agent: what it does, what input it expects,
and what it must pass on. For high security risk, include an agent whose job is to
inspect or validate other agents' output.

Return ONLY a JSON object in exactly this format:
{
  "topology_type": "Linear" or "Complete" or "Star",
  "reasoning": "<one or two sentences>",
  "agent_roles": {"<Agent>": "<role and instructions>"}
}
""",
            },
            {"role": "user", "content": prompt},
        ],
        format="json",
    )

    try:
        data = json.loads(response["message"]["content"])
        return data
    except json.JSONDecodeError:
        print("Failed to parse JSON response from Ollama.")
        return {}