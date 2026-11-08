import threading
import tkinter as tk
from tkinter import ttk
from orchestrator import get_agent_job_summaries


class AgentChatUI(tk.Tk):
    """Tkinter window to display agent interactions as styled chat boxes."""

    def __init__(self, title="Multi-Agent System Execution"):
        super().__init__()
        self.title(title)
        self.geometry("640x750")  # Fixed geometry string format
        self.configure(bg="#F4F6F8")

        # Header Title
        header = tk.Label(
            self,
            text="Agent Communication Monitor",
            font=("Segoe UI", 13, "bold"),
            bg="#2C3E50",
            fg="white",
            pady=12,
        )
        header.pack(fill=tk.X)

        # Scrollable Canvas Container
        self.canvas = tk.Canvas(self, bg="#F4F6F8", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F4F6F8")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Color mapping for distinct agents
        self.agent_colors = {}
        self.palette = [
            ("#E3F2FD", "#1565C0"),  # Blue
            ("#F3E5F5", "#7B1FA2"),  # Purple
            ("#E8F5E9", "#2E7D32"),  # Green
            ("#FFF3E0", "#E65100"),  # Orange
            ("#FCE4EC", "#C2185B"),  # Pink
            ("#E0F7FA", "#00838F"),  # Cyan
        ]

    def _get_agent_style(self, agent_id: str):
        if agent_id not in self.agent_colors:
            idx = len(self.agent_colors) % len(self.palette)
            self.agent_colors[agent_id] = self.palette[idx]
        return self.agent_colors[agent_id]

    def add_chat_bubble(self, sender: str, message: str, is_memory: bool = False):
        bg_color, accent_color = self._get_agent_style(sender)

        wrapper = tk.Frame(self.scrollable_frame, bg="#F4F6F8", pady=4)
        wrapper.pack(fill=tk.X, expand=True, padx=5)

        card_bg = "#E0E0E0" if is_memory else bg_color
        border_color = "#999999" if is_memory else accent_color

        card = tk.Frame(
            wrapper,
            bg=card_bg,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        card.pack(anchor="w", fill=tk.X)

        label_title = f"[{sender}] - Private Memory" if is_memory else f"[{sender}]"
        title_lbl = tk.Label(
            card,
            text=label_title,
            font=("Segoe UI", 9, "bold"),
            fg="#555555" if is_memory else accent_color,
            bg=card_bg,
            anchor="w",
        )
        title_lbl.pack(fill=tk.X)

        body_lbl = tk.Label(
            card,
            text=message,
            font=("Segoe UI", 10, "italic" if is_memory else "normal"),
            fg="#222222",
            bg=card_bg,
            justify=tk.LEFT,
            wraplength=540,
            anchor="w",
        )
        body_lbl.pack(fill=tk.X, pady=(4, 0))

        # Auto-scroll to latest message
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)


def run_system_with_ui(spec, agents, task, ui: AgentChatUI):
    """Identical to runner.run_system, but updates the GUI window live."""
    adjacency = spec["adjacency"]
    inbox = {agent_id: [] for agent_id in agents}
    inbox[spec["entry_agent"]].append(task)
    last_output = None

    for round_num in range(len(agents)):
        print(
            f"\n--- round {round_num} --- inboxes:"
            f" { {a: len(m) for a, m in inbox.items()} }"
        )
        outgoing = []

        for agent_id, agent in agents.items():
            if not inbox[agent_id]:
                continue

            messages = inbox[agent_id]
            inbox[agent_id] = []

            # Execute normal agent step
            output, is_final = agent.update_state(messages)

            # Extract memory note added in update_state
            memory_note = agent.memory_log[-1] if agent.memory_log else ""

            # Update UI chat boxes safely on main thread
            if memory_note:
                ui.after(0, ui.add_chat_bubble, agent_id, memory_note, True)
            ui.after(0, ui.add_chat_bubble, agent_id, output, False)

            if agent_id == spec["output_agent"]:
                last_output = output
                if is_final:
                    print("Final output reached by the output agent.")
                    return last_output

            # FIX: Use .get() to prevent KeyError if an agent is missing from adjacency list
            for target in adjacency.get(agent_id, []):
                outgoing.append((target, output))

        for target, message in outgoing:
            inbox[target].append(message)

        if not any(inbox.values()):
            break

    return last_output


def main():
    # Keep command prompt input identical
    task = input("Task: ")
    security = input("Security level (1-10): ").strip()

    # Orchestration and console logging identical
    spec, agents, task = get_agent_job_summaries(task, security)
    print("\nAdjacency list:", spec["adjacency"])
    print("Entry:", spec["entry_agent"], "| Output:", spec["output_agent"])

    # Create UI window
    ui = AgentChatUI(title=f"Multi-Agent Chat - {task[:30]}...")

    # Run system loop in background thread to keep UI interactive
    def background_runner():
        final = run_system_with_ui(spec, agents, task, ui)
        print("\nFINAL ANSWER:", final)

    thread = threading.Thread(target=background_runner, daemon=True)
    thread.start()

    # Launch Tkinter window loop
    ui.mainloop()


if __name__ == "__main__":
    main()