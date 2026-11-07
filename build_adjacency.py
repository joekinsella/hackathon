def format_adjacency_topology(raw_adjacency: dict) -> dict:
    """Takes the raw adjacency_list output from detail_job JSON and formats it into a clean graph structure,

    ensuring terminal nodes cleanly map to an empty list [].
    """
    topology = {}

    # Standardize agent keys and target lists
    for agent, targets in raw_adjacency.items():
        if isinstance(targets, list):
            topology[agent] = targets
        elif isinstance(targets, str):
            topology[agent] = [targets] if targets else []
        else:
            topology[agent] = []

    # Ensure any referenced target agent exists as a key (leaf nodes get [])
    all_targets = {
        target for targets in topology.values() for target in targets
    }
    for target in all_targets:
        if target not in topology:
            topology[target] = []

    return topology


def build_topology_from_details(design_data: dict) -> dict:
    """Extracts 'adjacency_list' from design_data and converts it to a standard topology graph.

    Falls back to a linear chain if adjacency_list was omitted.
    """
    raw_adjacency = design_data.get("adjacency_list", {})

    if not raw_adjacency and "agent_roles" in design_data:
        roles = list(design_data["agent_roles"].keys())
        raw_adjacency = {
            roles[i]: [roles[i + 1]] if i < len(roles) - 1 else []
            for i in range(len(roles))
        }

    return format_adjacency_topology(raw_adjacency)