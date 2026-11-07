from llm import prompt_llm

class Agent:
    def __init__(self, agent_id: str, role_description: str):
        self.agent_id = agent_id
        self.role_description = role_description
        self.memory_log = []
        self.output = ""
       

   
    #steps the agent. LLM is provided memory log and incoming message from other agent
    #after llm call, appends that rounds' context to memory log. Returns output for peer agent.
    def update_state(self, incoming_message: list) -> str:
        if self.memory_log:
            #format bulleted list 
            memory_context = "\n".join([f"• {m}" for m in self.memory_log])
        else:
            #**might not be necessary**
            memory_context = "Initial memory state is empty."

        system_prompt = f"""
        You are {self.agent_id}, acting as a {self.role_description}.
        You must respond using a JSON object containing exactly two keys:
        "public_message": Your public message to pass to peer agents.
        "private_memory": A concise note for yourself about what happened THIS round (under 100 words).
        """

        user_prompt = f"""
        Accumulated Private Memory (All Past Rounds):
        {memory_context}

        Incoming Message from Peer Agent:
        {incoming_message}
        """

        #Get JSON output from LLM
        data = prompt_llm(system_prompt, user_prompt)

        #Append the new note to memory list
        new_note = data.get("private_memory", "")
        if new_note:
            self.memory_log.append(new_note)

        peer_message = data.get("public_message", "")
        print(f"{self.agent_id} Saved Memory Note: '{new_note}'")
        print(f"{self.agent_id} Generated Public Message: '{peer_message}'")

        #return public message to be passed to neighbor agent(s)
        return peer_message