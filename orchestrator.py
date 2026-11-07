import json
import ollama
from agent import Agent

ORCHESTRATOR_PROMPT = """ You are a multi agent system Architect.
Given a USER TASK and a SECURITY RISK LEVEL (1-10), design a multi-agent system.

STEP 1: Choose a topology based strictly on security requirements:
- "Linear": Highest Security (8-10). Strict sequence of isolated stages to minimize attack surface and data leaks.
- "Star": Medium Security (4-7). A central coordinator delegates to isolated specialists and inspects messages.
- "Complete": Lowest Security (1-3). Fully interconnected mesh allowing unrestricted communication among all agents.

STEP 2: Define the agents.
Use 3 to 6 agents with descriptive names to quickly identify their roles and responsibilities.
Note, the agents must have actual names based on jobs, not just "agent 1, agent 2...", do not include the word agent in the name

TOPOLOGY RULES:

Linear: agents form one line. Each agent sends to exactly the next and previous agent.
The last agent has [second to last agent]. No agent has more than two target. The first and last agent have exactly one target

Star: ONE hub agent connects to every other agent. Spokes talk ONLY to the hub,
never to each other. The hub lists all spokes; each spoke lists only the hub.

Complete: all agents are connected to each other. Each agent lists all other agents as its targets.

The examples above only show the SHAPE. Use your own agent names that fit the task.
STEP 3: Define the adjacency list based on the chosen topology.
Example of linear:
{
  "AgentA": ["AgentB"],
  "AgentB": ["AgentA", "AgentC"],
  "AgentC": ["AgentB"]
}

Example of star:
{
  "HubAgent": ["AgentA", "AgentB", "AgentC"],
  "AgentA": ["HubAgent"],
  "AgentB": ["HubAgent"],
  "AgentC": ["HubAgent"]
}

Example of complete:
{
  "AgentA": ["AgentB", "AgentC"],
  "AgentB": ["AgentA", "AgentC"],
  "AgentC": ["AgentA", "AgentB"]
}

STEP 4: Write a role description for each agent: what it does, what input it expects,
and what it must pass on. For high security risk, include an agent whose job is to
inspect or validate other agents' output.

Return ONLY a JSON object in exactly this format:
{
  "topology_type": "Linear" or "Complete" or "Star",
  "adjacency_list" : {"<Agent>": ["<TargetAgent>", ...]},
  "reasoning": "<one or two sentences>",
  "agent_roles": {"<Agent>": "<role and instructions>"}
}
"""

def get_agent_job_summaries(task: str, security_score: str = "5") -> tuple:
    # CHANGED: topology is computed in code so the model can't ignore the thresholds
    level = int(security_score)
    topology = "Linear" if level >= 8 else "Star" if level >= 4 else "Complete"

    prompt = (f"Design a multi-agent system for task: '{task}' "
              f"with Security Level: {level}/10. "
              f"REQUIRED TOPOLOGY: {topology}. Do not choose a different one.")

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": ORCHESTRATOR_PROMPT},
            {"role": "user", "content": prompt},
        ],
        format="json",
    )

    # CHANGED: no try/except for now; a crash shows you what went wrong
    data = json.loads(response["message"]["content"])
    print("Orchestrator output:", json.dumps(data, indent=2))   # handy while debugging

    adjacency = data["adjacency_list"]
    roles = data["agent_roles"]
    names = list(adjacency)

    # NEW: entry/output agents aren't in the JSON, so derive them
    if data["topology_type"] == "Star":
        entry = max(adjacency, key=lambda a: len(adjacency[a]))   # the hub
        output = entry
    else:                                                          # Linear or Complete
        entry = names[0]
        output = names[-1]

    spec = {
        "adjacency": adjacency,
        "entry_agent": entry,
        "output_agent": output,
    }
    agents = {name: Agent(name, desc) for name, desc in roles.items()}

    return spec, agents, task

