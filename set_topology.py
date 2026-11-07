import build_topos


def set_topology(agent_list: list, topology_type: str) -> dict:
    """Takes a list of agent names (or Agent objects) and a topology type ('Linear'/'Chain', 'Star', 'Complete'),

    and returns an adjacency dictionary representing the network topology.
    """
    # Extract string names whether passed a list of strings or Agent objects
    names = [
        agent.agent_id if hasattr(agent, "agent_id") else str(agent)
        for agent in agent_list
    ]
    length = len(names)
    topo_lower = topology_type.lower()

    # Call the build_topos helper based on topology_type
    if "star" in topo_lower:
        index_map = build_topos.create_star(length)
    elif "linear" in topo_lower or "chain" in topo_lower:
        index_map = build_topos.build_linear(length)
    elif "complete" in topo_lower:
        index_map = build_topos.build_complete(length)
    else:
        index_map = build_topos.build_linear(length)

    # Map numeric index graph to agent names
    topology_dict = {}
    for idx, name in enumerate(names):
        target_indices = index_map.get(idx, [])
        topology_dict[name] = [names[i] for i in target_indices]

    return topology_dict