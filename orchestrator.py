import json
from agent import Agent
from hosted_llm import prompt_hosted

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

    data = prompt_hosted(ORCHESTRATOR_PROMPT, prompt)
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