import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

# Import your existing orchestrator and runner
from orchestrator_3 import get_agent_job_summaries
from runner import run_system

# Distinct color palette for agents
AGENT_COLORS = [
    "#00E676",  # Neon Green
    "#29B6F6",  # Light Blue
    "#FF7043",  # Deep Coral
    "#AB47BC",  # Purple
    "#FFCA28",  # Amber Gold
    "#EC407A",  # Hot Pink
    "#26A69A",  # Teal
    "#FF5252",  # Bright Red
]


class AgentLogGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Agent System — Real-Time Monitor")
        self.root.geometry("900x700")
        self.root.configure(bg="#1E1E1E")

        self.msg_queue = queue.Queue()
        self.agent_color_map = {}
        self.color_index = 0

        self._build_ui()
        self.root.after(100, self._process_queue)

    def _build_ui(self):
        # Top Input Controls Frame
        control_frame = tk.Frame(self.root, bg="#2D2D2D", padding=10)
        control_frame = tk.Frame(self.root, bg="#2D2D2D")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Task Input
        tk.Label(
            control_frame,
            text="Task:",
            fg="#FFFFFF",
            bg="#2D2D2D",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        self.task_entry = tk.Entry(
            control_frame,
            bg="#3D3D3D",
            fg="#FFFFFF",
            insertbackground="white",
            font=("Consolas", 10),
            width=50,
        )
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.insert(
            0, "Build a secure React calculator app with dark mode"
        )

        # Security Level Input
        tk.Label(
            control_frame,
            text="Security (1-10):",
            fg="#FFFFFF",
            bg="#2D2D2D",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        self.sec_entry = tk.Entry(
            control_frame,
            bg="#3D3D3D",
            fg="#FFFFFF",
            insertbackground="white",
            font=("Consolas", 10),
            width=5,
        )
        self.sec_entry.pack(side=tk.LEFT, padx=5)
        self.sec_entry.insert(0, "5")

        # Start Button
        self.start_btn = tk.Button(
            control_frame,
            text="Run System",
            bg="#007ACC",
            fg="#FFFFFF",
            activebackground="#005999",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            command=self.start_execution,
        )
        self.start_btn.pack(side=tk.LEFT, padx=15)

        # Real-time Stream Terminal Window
        self.log_area = scrolledtext.ScrolledText(
            self.root,
            bg="#121212",
            fg="#CCCCCC",
            font=("Consolas", 10),
            wrap=tk.WORD,
            padx=10,
            pady=10,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Tag configuration for default system messages
        self.log_area.tag_config(
            "SYSTEM", foreground="#888888", font=("Consolas", 9, "italic")
        )
        self.log_area.tag_config(
            "HEADER", foreground="#FFFFFF", font=("Consolas", 10, "bold")
        )
        self.log_area.tag_config(
            "FINAL", foreground="#00FFCC", font=("Consolas", 11, "bold")
        )

    def get_agent_color(self, agent_id):
        """Assigns a persistent unique color to each agent."""
        if agent_id not in self.agent_color_map:
            color = AGENT_COLORS[self.color_index % len(AGENT_COLORS)]
            self.agent_color_map[agent_id] = color
            self.color_index += 1
            # Dynamically register new tag in Tkinter text widget
            self.log_area.tag_config(
                agent_id, foreground=color, font=("Consolas", 10, "bold")
            )
        return agent_id

    def log_event(self, agent_id, round_num, message, memory, is_final):
        """Pushes events into thread-safe queue."""
        self.msg_queue.put((agent_id, round_num, message, memory, is_final))

    def _process_queue(self):
        """Reads logs from queue and updates the UI on main thread."""
        while not self.msg_queue.empty():
            item = self.msg_queue.get()

            if item[0] == "__SYSTEM__":
                self.log_area.insert(
                    tk.END, f"\n[SYSTEM] {item[2]}\n", "SYSTEM"
                )
            elif item[0] == "__FINAL__":
                self.log_area.insert(
                    tk.END,
                    f"\n\n=========================================="
                    f"\nFINAL SYSTEM RESULT:\n{item[2]}"
                    f"\n==========================================\n",
                    "FINAL",
                )
            else:
                agent_id, round_num, message, memory, is_final = item
                tag = self.get_agent_color(agent_id)

                self.log_area.insert(
                    tk.END,
                    f"\n------------------------------------------\n",
                    "SYSTEM",
                )
                self.log_area.insert(
                    tk.END,
                    f"[{agent_id}] (Round {round_num})\n",
                    tag,
                )
                self.log_area.insert(
                    tk.END, f"Memory: {memory}\n", "SYSTEM"
                )
                self.log_area.insert(
                    tk.END, f"Output:\n{message}\n", "HEADER"
                )
                if is_final:
                    self.log_area.insert(
                        tk.END, f"STATUS: [IS_FINAL = TRUE]\n", "FINAL"
                    )

            self.log_area.see(tk.END)

        self.root.after(50, self._process_queue)

    def start_execution(self):
        task = self.task_entry.get().strip()
        security = self.sec_entry.get().strip()

        if not task:
            return

        self.start_btn.config(state=tk.DISABLED)
        self.log_area.delete("1.0", tk.END)
        self.msg_queue.put(
            ("__SYSTEM__", 0, f"Initializing system for task: '{task}'...", "", False)
        )

        # Run multi-agent execution in background thread
        thread = threading.Thread(
            target=self._run_thread, args=(task, security), daemon=True
        )
        thread.start()

    def _run_thread(self, task, security):
        try:
            spec, agents, task = get_agent_job_summaries(task, security)
            self.msg_queue.put(
                (
                    "__SYSTEM__",
                    0,
                    f"Topology: {spec.get('topology_type', 'N/A')} | Entry: {spec['entry_agent']} | Output: {spec['output_agent']}",
                    "",
                    False,
                )
            )

            final_result = run_system(
                spec, agents, task, callback=self.log_event
            )
            self.msg_queue.put(
                ("__FINAL__", 0, str(final_result), "", True)
            )

        except Exception as e:
            self.msg_queue.put(
                ("__SYSTEM__", 0, f"Execution Error: {e}", "", False)
            )
        finally:
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = AgentLogGUI(root)
    root.mainloop()