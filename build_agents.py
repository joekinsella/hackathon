#NOT USELESS
"""


def create_agent_network(design_data: dict) -> dict[str, Agent]:

    agent_roles = design_data.get("agent_roles", {})

    agents = {}
    for agent_name, role_desc in agent_roles.items():
        agents[agent_name] = Agent(
            agent_id=agent_name, role_description=role_desc
        )

    return agents
"""