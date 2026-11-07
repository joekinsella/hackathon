from llm import prompt_llm

AGENT_PROMPT = """You are {agent_id}, acting as: {role_description}.

OVERALL TASK: {task}
You can send messages to: {neighbors}

Each turn you receive messages from other agents. Do your part of the task,
then write a message for your neighbors that moves the task forward.
Do not repeat what you were told. Add something new.

Respond with a JSON object with exactly two keys:
"public_message": your work product or request for your neighbors.
"private_memory": one or two sentences on what you did this turn.
"""


class Agent:
    def __init__(self, agent_id: str, role_description: str, task: str, neighbors: list):
        self.agent_id = agent_id
        self.role_description = role_description
        self.task = task
        self.neighbors = neighbors
        self.memory_log = []

        # fixed for the whole run, so build it once
        self.system_prompt = AGENT_PROMPT.format(
            agent_id=self.agent_id,
            role_description=self.role_description,
            task=self.task,
            neighbors=", ".join(self.neighbors) if self.neighbors else "no neighbors. (you give the final answer)",
        )

    def update_state(self, incoming_messages: list) -> str:
        memory_context = "\n".join(f"• {m}" for m in self.memory_log) or "Nothing yet."
        incoming = "\n".join(f"- {m}" for m in incoming_messages)

        user_prompt = f"""Your memory from past turns:
{memory_context}

Incoming messages:
{incoming}"""

        data = prompt_llm(self.system_prompt, user_prompt)

        new_note = data.get("private_memory", "")
        if new_note:
            self.memory_log.append(new_note)

        peer_message = data.get("public_message", "")
        print(f"{self.agent_id} Saved Memory Note: '{new_note}'")
        print(f"{self.agent_id} Generated Public Message: '{peer_message}'")
        return peer_message