from orchestrator import get_agent_job_summaries
from runner import run_system

if __name__ == "__main__":
    task = input("Task: ")
    security = input("Security level (1-10): ").strip()

    spec, agents, task = get_agent_job_summaries(task, security)
    print("\nAdjacency list:", spec["adjacency"])
    print("Entry:", spec["entry_agent"], "| Output:", spec["output_agent"])

    final = run_system(spec, agents, task)
    print("\nFINAL ANSWER:", final)

    