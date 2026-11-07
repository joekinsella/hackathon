import build_agents
import detail_job
from build_specs import create_spec_dict
from set_topology import build_topology_from_details


def main():
    #task = input("Enter a task for an AI agent system: ").strip()
    task = "make an ai that cracks an encoded message"
    security = input(
        "On a scale of 1-10, how important is security? "
    ).strip()

    print("Waiting for design data...")
    design_data = detail_job.get_agent_job_summaries(task, security)
    roles_dict = design_data.get("agent_roles", {})
    topology_type = design_data.get("topology_type", "Linear")

    # Generate adjacency dict
    adjacency_dict = build_topology_from_details(design_data)

    # Create Spec instance
    spec_dict = create_spec_dict(adjacency_dict, roles_dict)

    print("\n--- Spec Dictionary ---")
    print(spec_dict)
    print(f"Entry Agent:  {spec_dict['entry']}")
    print(f"Output Agent: {spec_dict['output']}")


if __name__ == "__main__":
    main()