from hosted_llm import prompt_hosted as prompt_llm

AGENT_PROMPT = """You are {agent_id}, acting as: {role_description}.

OVERALL TASK: {task}
You can send messages to: {neighbors}

Each turn you receive messages from other agents. Do your part of the task,
then write a message for your neighbors that moves the task forward.
Do not repeat what you were told. Add something new.

Respond with a JSON object with exactly three keys:
"public_message": your work product or request for your neighbors.
"private_memory": one or two sentences on what you did this turn.
"is_final": see rules below.
RULES FOR is_final: - Set "is_final" to true ONLY if ALL of these are true:
0. Your output is delivered directly to the user do not address other agents or ask for reviews
1. You are the agent responsible for the final answer. 
2. Your public_message IS the complete final answer to the overall task, ready to hand to the user as-is. 
3. Your public_message asks nothing of anyone. It contains no requests, questions, or review steps. 
4. You have already received and used the input you needed from your neighbors. 
- If you want something checked, reviewed, or revised, set "is_final" to false and put the request in public_message. 
- If you are unsure, set "is_final" to false. 
- Never set "is_final" to true on a message that asks another agent to do something.
"""


class Agent:

    def __init__(
        self, agent_id: str, role_description: str, task: str, neighbors: list
    ):
        self.agent_id = agent_id
        self.role_description = role_description
        self.task = task
        self.neighbors = neighbors
        self.memory_log = []
        self.sent = []

        self.system_prompt = AGENT_PROMPT.format(
            agent_id=self.agent_id,
            role_description=self.role_description,
            task=self.task,
            neighbors=", ".join(self.neighbors)
            if self.neighbors
            else "no neighbors. (you give the final answer)",
        )

    def update_state(self, incoming_messages: list) -> tuple:
        memory_context = (
            "\n".join(f"• {m}" for m in self.memory_log) or "Nothing yet."
        )
        incoming = "\n".join(f"- {m}" for m in incoming_messages)

        user_prompt = f"""Your memory from past turns:
{memory_context}

Incoming messages:
{incoming}"""

        data = prompt_llm(self.system_prompt, user_prompt)

        # Handle edge case where LLM returns a list or non-dict JSON structure
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            data = data[0]
        elif not isinstance(data, dict):
            data = {
                "public_message": str(data),
                "private_memory": "Extracted output from non-dict response.",
                "is_final": False,
            }

        new_note = data.get("private_memory", "")
        if new_note:
            self.memory_log.append(new_note)

        peer_message = data.get("public_message", "")
        is_final = data.get("is_final", False) is True

        self.sent.append(peer_message)

        print(f"{self.agent_id} Saved Memory Note: '{new_note}'")
        print(f"{self.agent_id} Generated Public Message: '{peer_message}'")
        return peer_message, is_final