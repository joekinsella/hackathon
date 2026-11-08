import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

# Distinct background colors assigned to agents
AGENT_COLOR_PALETTE = [
    "#D0E8FF",  # Soft Blue
    "#D4EDDA",  # Soft Green
    "#FFF3CD",  # Soft Yellow
    "#F8D7DA",  # Soft Pink/Red
    "#E2D9F3",  # Soft Purple
    "#FFE5D9",  # Soft Peach
    "#E0F7FA",  # Soft Teal
]


def run_system_gui(spec: dict, agents: dict, task: str):
    """Launches a Tkinter window and streams agent execution outputs in real time."""
    root = tk.Tk()
    root.title("Multi-Agent Architecture Execution")
    root.geometry("960x750")

    # Header banner
    header_frame = ttk.Frame(root, padding=10)
    header_frame.pack(fill=tk.X)

    ttk.Label(
        header_frame,
        text=f"Task: {task}",
        font=("Segoe UI", 11, "bold"),
        wraplength=900,
    ).pack(anchor="w")
    ttk.Label(
        header_frame,
        text=f"Entry Agent: {spec['entry_agent']}  |  Output Agent: {spec['output_agent']}",
        font=("Segoe UI", 9, "italic"),
    ).pack(anchor="w")

    # Scrollable output log area
    output_box = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, font=("Consolas", 10), padx=10, pady=10
    )
    output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Assign each agent a unique background color tag
    for idx, agent_id in enumerate(agents.keys()):
        color = AGENT_COLOR_PALETTE[idx % len(AGENT_COLOR_PALETTE)]
        tag_name = f"tag_{agent_id}"

        output_box.tag_config(
            tag_name,
            background=color,
            foreground="#111111",
            lmargin1=15,
            lmargin2=25,
            rmargin=15,
            spacing1=6,
            spacing3=10,
        )

    # Tag configuration for final completion banner
    output_box.tag_config(
        "tag_final",
        background="#28a745",
        foreground="#ffffff",
        font=("Consolas", 11, "bold"),
        lmargin1=15,
        rmargin=15,
        spacing1=10,
        spacing3=10,
    )

    msg_queue = queue.Queue()

    def worker():
        """Background thread running the LLM execution pipeline without freezing the UI."""
        adjacency = spec["adjacency"]
        inbox = {agent_id: [] for agent_id in agents}  # Mailbox per agent[cite: 17]
        inbox[spec["entry_agent"]].append(task)  # Initial user task[cite: 17]
        last_output = None
        max_rounds = len(agents) * 3  # Sufficient rounds for multi-pass tasks

        for round_num in range(max_rounds):
            outgoing = []

            for agent_id, agent in agents.items():
                if not inbox[agent_id]:
                    continue

                messages = inbox[agent_id]
                inbox[agent_id] = []  # Clear inbox[cite: 17]

                # Run agent LLM query[cite: 12]
                output, is_final = agent.update_state(messages)

                # Send real-time message payload to GUI thread
                msg_queue.put(("OUTPUT", round_num, agent_id, output))

                if agent_id == spec["output_agent"]:
                    last_output = output
                    if is_final:
                        msg_queue.put(
                            ("FINAL", f"FINAL ANSWER REACHED:\n{output}")
                        )
                        return

                for target in adjacency.get(agent_id, []):
                    outgoing.append((target, output))

            for target, message in outgoing:
                inbox[target].append(message)

            if not any(inbox.values()):
                break

        msg_queue.put(
            ("FINAL", f"FINAL ANSWER (Pipeline Completed):\n{last_output}")
        )

    def poll_queue():
        """Processes incoming agent responses from the background queue every 100ms."""
        try:
            while True:
                msg_type, *args = msg_queue.get_nowait()

                if msg_type == "OUTPUT":
                    round_num, agent_id, output = args
                    tag_name = f"tag_{agent_id}"

                    header = f"--- [Round {round_num}] AGENT: {agent_id} ---\n"
                    body = f"{header}{output}\n"

                    output_box.insert(tk.END, body, tag_name)
                    output_box.insert(tk.END, "\n")
                    output_box.see(tk.END)

                elif msg_type == "FINAL":
                    final_text = args[0]
                    banner = f"\n========================================\n{final_text}\n========================================\n"
                    output_box.insert(tk.END, banner, "tag_final")
                    output_box.see(tk.END)

        except queue.Empty:
            pass

        root.after(100, poll_queue)

    # Start background execution thread
    threading.Thread(target=worker, daemon=True).start()

    # Start polling loop and show window
    root.after(100, poll_queue)
    root.mainloop()