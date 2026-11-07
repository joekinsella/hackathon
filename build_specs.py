
class Agent:

    def __init__(self, agent_id: str, role_description: str):
        self.agent_id = agent_id
        self.role_description = role_description
        self.memory_log = []
        self.output = ""

    def __repr__(self):
        return f"Agent('{self.agent_id}', '{self.role_description}')"

def create_spec_dict(adjacency_dict: dict, roles_desc_dict: dict) -> dict:
    """Creates a spec dictionary containing adjacency graph, role descriptions,

    and the first/last Agent instances.
    """
    agent_names = list(adjacency_dict.keys())

    if not agent_names:
        return {}

    # First agent in list -> entry Agent
    entry_name = agent_names[0]
    entry_agent = Agent(
        agent_id=entry_name,
        role_description=roles_desc_dict.get(entry_name, ""),
    )

    # Last agent in list -> output Agent
    output_name = agent_names[-1]
    output_agent = Agent(
        agent_id=output_name,
        role_description=roles_desc_dict.get(output_name, ""),
    )

    return {
        "adjacency_dict": adjacency_dict,
        "role_description": roles_desc_dict,
        "entry": entry_agent,
        "output": output_agent,
    }