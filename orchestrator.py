import json
from agent import Agent
from hosted_llm import prompt_hosted

ORCHESTRATOR_PROMPT = """ 
You are a multi-agent system architect.
Given a USER TASK and a SECURITY LEVEL (1-10), choose a topology and design the agents.

STEP 1: Security level limits your choice. Apply it first.
- 8-10: you MUST use "Linear". Messages travel one way only, so a compromised agent
  can only affect agents after it. Break the task into sequential stages.
- 4-7: choose "Linear" or "Star" by task fit. Never "Complete".
- 1-3: choose any topology by task fit.

STEP 2: Match the topology to the task.
- "Linear": a strict pipeline where each stage needs the previous stage's finished output
  (draft -> edit -> proofread; extract -> clean -> analyze -> report).
- "Star": one coordinator splits the work into independent subtasks, sends them to
  specialists, and combines the results (compare options, research from several angles).
- "Complete": open-ended discussion where every agent must react to every other agent
  (debate, brainstorm, consensus). Poor fit for sensitive input or more than 4 agents.
If more than one fits, pick the simplest.

STEP 3: Define 3 to 5 agents.
- Names are job-based CamelCase with no spaces and no word "Agent".
- Each role says what the agent receives, does, and passes on. The flow must match the adjacency list.
- Copy each name EXACTLY everywhere. "adjacency_list" and "agent_roles" must have the same keys,
  and every name in an adjacency list must be a key in "agent_roles".

STEP 4: Build the adjacency list. adjacency_list[X] = the agents X may send messages to.
- Linear: list agents in workflow order. Each lists ONLY the next agent. The last has [].
  Example: {"A": ["B"], "B": ["C"], "C": []}
- Star: the hub is listed FIRST and lists every spoke. Each spoke lists ONLY the hub.
  Example: {"Hub": ["A", "B"], "A": ["Hub"], "B": ["Hub"]}
- Complete: every agent lists every other agent, never itself.
  Example: {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
The examples show shape only. Use your own names.

Return ONLY this JSON:
{
  "topology_type": "Linear" or "Star" or "Complete",
  "adjacency_list": {"<Agent>": ["<TargetAgent>", ...]},
  "reasoning": "<one sentence>",
  "agent_roles": {"<Agent>": "<role>"}
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