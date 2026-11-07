import json
import requests

print("FILE STARTED", flush=True)

#enforce llm to respond with json so that can process by json keys
def prompt_llm(system_prompt: str, user_prompt: str) -> dict:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.2",
        "messages": [
            #system pr0mpt injects in header
            {"role": "system", "content": system_prompt},
            #user_pr0mpt reads similar to human entry
            {"role": "user", "content": user_prompt}
        ],
        "format": "json",
        "stream": False
    }
    try:
        # Added timeout=60 so it doesn't hang forever if Ollama is unresponsive
        response = requests.post(url, json=payload, timeout=60).json()
        return json.loads(response["message"]["content"])
    except requests.exceptions.ConnectionError:
        print("\n ERROR: Could not connect to Ollama. Make sure Ollama is running ('ollama serve')!")
        raise
    except Exception as e:
        print(f"\n ERROR parsing LLM response: {e}")
        return {"public_message": "Error processing task.", "private_memory": "Failed step."}


class Agent:
    def __init__(self, agent_id: str, role_description: str):
        self.agent_id = agent_id
        self.role_description = role_description
        self.memory_log = []
        self.output = ""
       

   
    #steps the agent. LLM is provided memory log and incoming message from other agent
    #after llm call, appends that rounds' context to memory log. Returns output for peer agent.
    def update_state(self, incoming_message: str) -> str:
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

Chain_Topology = {
    "Agent_0": ["Agent_1"],
    "Agent_1": ["Agent_2"],
    "Agent_2": []
}

agents = {
    "Agent_0": Agent("Agent_0", "job"),
    "Agent_1": Agent("Agent_1", "job"),
    "Agent_2": Agent("Agent_2", "job")
}
if __name__ == "__main__":
    print("Starting pipeline!!")
    current_message = "Description of task for 1st agent "
    for sender_id in Chain_Topology:
        agent = agents[sender_id]
        
        public_output = agent.update_state(incoming_message = current_message)
        
        current_message = public_output
