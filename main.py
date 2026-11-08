import threading
from orchestrator import get_agent_job_summaries
from runner_ui import AgentChatUI, run_system_with_ui

if __name__ == "__main__":
    task = input("Task: ")
    security = input("Security level (1-10): ").strip()

    spec, agents, task = get_agent_job_summaries(task, security)
    print("\nAdjacency list:", spec["adjacency"])
    print("Entry:", spec["entry_agent"], "| Output:", spec["output_agent"])

    # Launch GUI Window & Render Topology Graph
    ui = AgentChatUI(title=f"Multi-Agent System - {task[:30]}...")
    ui.draw_topology(spec, agents)

    # Run execution loop in background thread to keep GUI responsive
    def background_runner():
        final = run_system_with_ui(spec, agents, task, ui)
        print("\nFINAL ANSWER:", final)

    thread = threading.Thread(target=background_runner, daemon=True)
    thread.start()

    # Start Tkinter main loop
    ui.mainloop()