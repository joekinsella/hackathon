class Agent:

    def __init__(self, agent_id: str, role_description: str):
        self.agent_id = agent_id
        self.role_description = role_description
        self.memory_log = []
        self.output = ""

    def __repr__(self):
        return f"Agent('{self.agent_id}', '{self.role_description}')"


def create_agent_network(design_data: dict) -> dict[str, Agent]:
    """Instantiates Agent objects using the design_data roles from Ollama."""
    agent_roles = design_data.get("agent_roles", {})

    agents = {}
    for agent_name, role_desc in agent_roles.items():
        agents[agent_name] = Agent(
            agent_id=agent_name, role_description=role_desc
        )

    return agents