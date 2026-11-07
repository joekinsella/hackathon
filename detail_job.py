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
                "content": """You are a Multi-Agent System Architect.
Given a USER TASK and a SECURITY RISK LEVEL, design a multi-agent system.

STEP 1: Check the security risk level FIRST.
- "low" risk: choose the topology purely by task fit (Step 2).
- "medium" risk: choose by task fit (Step 2), but if two topologies fit equally well,
  prefer the one with fewer communication edges.
- "high" risk: you MUST use "Chain", even if another topology fits the task better.
  Skip the topology choice in Step 2 and go straight to Step 3.

STEP 2: Choose one of the three following topologies.

"Chain" is best for tasks that are a strict pipeline, where each stage needs the finished output of the previous stage and stages do not need to talk back.
  Good fits: draft -> edit -> proofread; extract data -> clean data -> analyze -> report;
  write code -> test code -> document code; translate -> review -> format.
  Signs: the task contains words like "then", "after that", "once finished"; the order of the work is fixed.
  Poor fit: tasks where several pieces of work can happen independently, or where results must be revised repeatedly.

"Star" is best for tasks where one coordinator splits the work into independent subtasks, sends them to specialists, and combines the results.
  Good fits: research a topic from several angles and merge the findings; compare several products or options;
  answer a question that needs a calculator, a searcher, and a writer; process many similar items in parallel.
  Signs: the subtasks do not depend on each other; one agent must see everything to produce the final answer.
  Poor fit: strict pipelines (use Chain), or large tasks needing multiple layers of management (use Hierarchical).

"Hierarchical" is best for large or complex tasks that split into sub-teams, each with its own specialists, or that need review and approval at several levels.
  Good fits: build a full software project (architect -> frontend lead and backend lead -> their workers);
  produce a long report with separate sections handled by separate teams; any task needing a manager to approve work before it moves up.
  Signs: the task has several major components, each of which would itself need multiple steps.
  Poor fit: small tasks. Do not use Hierarchical when 3 agents would do the job.

If the task fits more than one topology, pick the simplest one that works.

STEP 3: Define the agents.
Use 3 to 6 agents with descriptive names like "Planner", "Coder", "Inspector".
Every agent name MUST appear as a key in BOTH "adjacency_list" and "agent_roles".

STEP 4: Build the adjacency list.
adjacency_list[X] = the list of agents that X is ALLOWED TO SEND messages to.
An edge is one-directional. If X may send to Y and Y may reply to X, BOTH must be listed.
An agent that sends to no one gets an empty list [].
Only use agent names that you defined. Never list an agent as its own target.

TOPOLOGY RULES:

Chain: agents form one line. Each agent sends to exactly the next agent.
The last agent has []. No agent has more than one target. No replies backward.
Example (Planner -> Coder -> Reviewer):
{"Planner": ["Coder"], "Coder": ["Reviewer"], "Reviewer": []}

Star: ONE hub agent connects to every other agent. Spokes talk ONLY to the hub,
never to each other. The hub lists all spokes; each spoke lists only the hub.
Example (hub is Coordinator):
{"Coordinator": ["Researcher", "Writer", "Checker"], "Researcher": ["Coordinator"], "Writer": ["Coordinator"], "Checker": ["Coordinator"]}

Hierarchical: a tree with one root. Each parent sends to its own children,
and each child sends back ONLY to its own parent. No links between siblings
and no links that skip a level.
Example (Director manages Lead_A and Lead_B; Lead_A manages Worker_1 and Worker_2):
{"Director": ["Lead_A", "Lead_B"], "Lead_A": ["Director", "Worker_1", "Worker_2"], "Lead_B": ["Director"], "Worker_1": ["Lead_A"], "Worker_2": ["Lead_A"]}

The examples above only show the SHAPE. Use your own agent names that fit the task.

STEP 4: Write a role description for each agent: what it does, what input it expects,
and what it must pass on. For high security risk, include an agent whose job is to
inspect or validate other agents' output.

Return ONLY a JSON object in exactly this format:
{
  "topology_type": "Chain" or "Star" or "Hierarchical",
  "reasoning": "<one or two sentences>",
  "adjacency_list": {"<Agent>": ["<Agent>", ...]},
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
        return data.get("jobs", [])
    except json.JSONDecodeError:
        print("Failed to parse JSON response from Ollama.")
        return []