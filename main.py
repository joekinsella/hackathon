from orchestrator import get_agent_job_summaries
from runner_ui import run_system_gui
# Optional fallback if you ever want to run without UI:
# from runner import run_system

if __name__ == "__main__":
    task = input("Task: ")
    security = input("Security level (1-10): ").strip()

    # Generate multi-agent topology specification
    spec, agents, task = get_agent_job_summaries(task, security)
    
    # Original terminal diagnostics
    print("\nAdjacency list:", spec["adjacency"])
    print("Entry:", spec["entry_agent"], "| Output:", spec["output_agent"])

    print("\nLaunching execution window...")
    
    # Runs the real-time UI window and returns the final answer upon completion
    final = run_system_gui(spec, agents, task)
    
    # Original final answer terminal output
    print("\nFINAL ANSWER:\n", final)