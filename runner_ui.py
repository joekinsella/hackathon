import math
import threading
import tkinter as tk
from tkinter import ttk
from orchestrator import get_agent_job_summaries


def detect_topology_info(spec: dict) -> tuple:
    """Analyzes spec['adjacency'] directly without modifying spec."""
    adjacency = spec.get("adjacency", {})
    nodes = list(adjacency.keys())
    n = len(nodes)

    if n == 0:
        return "Unknown Topology", "No graph nodes detected."

    total_edges = sum(len(targets) for targets in adjacency.values())
    max_out = max((len(targets) for targets in adjacency.values()), default=0)

    # Check for Complete graph
    if n > 1 and total_edges >= n * (n - 1):
        return (
            "Complete Topology",
            "Fully connected peer-to-peer network for maximum cross-validation and parallel discussion.",
        )

    # Check for Star graph
    if max_out >= n - 1 or any(
        len(targets) == n - 1 for targets in adjacency.values()
    ):
        return (
            "Star Topology",
            "Central hub agent routes tasking and aggregates feedback across specialized spoke agents.",
        )

    # Check for Linear graph
    if all(len(targets) <= 1 for targets in adjacency.values()):
        return (
            "Linear Topology",
            "Sequential step-by-step assembly line ensuring focused handoffs and strict validation.",
        )

    return (
        "Custom Topology",
        "Tailored multi-agent routing graph designed specifically for this workflow.",
    )


class AgentChatUI(tk.Tk):
    """Tkinter window to display agent interactions, topology graph, and final answer."""

    def __init__(self, title="Multi-Agent System Execution"):
        super().__init__()
        self.title(title)
        self.geometry("1100x880")
        self.configure(bg="#F4F6F8")

        # Top Header Title
        header = tk.Label(
            self,
            text="Multi-Agent Orchestration & Communication Monitor",
            font=("Segoe UI", 13, "bold"),
            bg="#2C3E50",
            fg="white",
            pady=10,
        )
        header.pack(fill=tk.X)

        # MAIN CONTAINER (Split into Chat & Right Topology Panel)
        main_container = tk.Frame(self, bg="#F4F6F8")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # LEFT PANEL: Scrollable Chat Log
        left_frame = tk.Frame(main_container, bg="#F4F6F8")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left_frame, bg="#F4F6F8", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.canvas.yview
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
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # RIGHT PANEL: System Topology Graph & Architecture
        right_frame = tk.LabelFrame(
            main_container,
            text=" System Architecture ",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#2C3E50",
            padx=10,
            pady=10,
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # Shape Title (Above Diagram)
        self.topo_shape_lbl = tk.Label(
            right_frame,
            text="Topology: Analyzing...",
            font=("Segoe UI", 11, "bold"),
            fg="#1565C0",
            bg="#FFFFFF",
            anchor="w",
        )
        self.topo_shape_lbl.pack(fill=tk.X, pady=(0, 2))

        # Reasoning Subtitle (Smaller text)
        self.topo_reason_lbl = tk.Label(
            right_frame,
            text="Architecture reasoning loading...",
            font=("Segoe UI", 8, "italic"),
            fg="#555555",
            bg="#FFFFFF",
            justify=tk.LEFT,
            wraplength=300,
            anchor="w",
        )
        self.topo_reason_lbl.pack(fill=tk.X, pady=(0, 8))

        # Topology Canvas
        self.graph_canvas = tk.Canvas(
            right_frame, width=320, height=420, bg="#FAFAFA", highlightthickness=1
        )
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)

        # BOTTOM PANEL: Final Answer Box with Vertical Scrollbar
        bottom_frame = tk.LabelFrame(
            self,
            text=" Final Answer (Auto-copied to Clipboard) ",
            font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            padx=10,
            pady=8,
        )
        bottom_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        text_container = tk.Frame(bottom_frame, bg="#FFFFFF")
        text_container.pack(fill=tk.BOTH, expand=True)

        answer_scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        self.final_answer_text = tk.Text(
            text_container,
            height=10,
            font=("Consolas", 9),
            bg="#F8F9FA",
            fg="#111111",
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=8,
            pady=8,
            yscrollcommand=answer_scrollbar.set,
        )
        answer_scrollbar.config(command=self.final_answer_text.yview)

        self.final_answer_text.insert(
            "1.0",
            "Executing multi-agent task... Final answer will appear here once ready.",
        )
        self.final_answer_text.config(state=tk.DISABLED)

        self.final_answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        answer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Color mapping and infection tracking
        self.agent_colors = {}
        self.palette = [
            ("#E3F2FD", "#1565C0"),  # Blue
            ("#F3E5F5", "#7B1FA2"),  # Purple
            ("#E8F5E9", "#2E7D32"),  # Green
            ("#FFF3E0", "#E65100"),  # Orange
            ("#FCE4EC", "#C2185B"),  # Pink
            ("#E0F7FA", "#00838F"),  # Cyan
        ]

        self.node_positions = {}
        self.node_items = {}
        self.infected_nodes = set()
        self.infected_rings = {}

    def _get_agent_style(self, agent_id: str):
        if agent_id not in self.agent_colors:
            idx = len(self.agent_colors) % len(self.palette)
            self.agent_colors[agent_id] = self.palette[idx]
        return self.agent_colors[agent_id]

    def mark_node_infected(self, agent_id: str):
        """Draws a red ring around an infected node and updates its colors."""
        if agent_id not in self.node_positions:
            return

        self.infected_nodes.add(agent_id)
        x, y = self.node_positions[agent_id]
        node_radius = 24

        # Draw red outer halo circle around the node
        if agent_id not in self.infected_rings:
            ring = self.graph_canvas.create_oval(
                x - node_radius - 6,
                y - node_radius - 6,
                x + node_radius + 6,
                y + node_radius + 6,
                outline="#D32F2F",
                width=3,
            )
            self.infected_rings[agent_id] = ring

        # Update node palette colors to red theme
        if agent_id in self.node_items:
            circle, _, _ = self.node_items[agent_id]
            infected_bg = "#FFCDD2"
            infected_accent = "#B71C1C"
            self.node_items[agent_id] = (circle, infected_bg, infected_accent)
            self.graph_canvas.itemconfig(
                circle, fill=infected_bg, outline=infected_accent, width=3
            )

    def draw_topology(self, spec: dict, agents: dict):
        """Renders topology headers, graph nodes, and directed arrows."""
        self.graph_canvas.delete("all")
        self.infected_rings.clear()

        shape_name, reasoning_text = detect_topology_info(spec)
        self.topo_shape_lbl.config(text=f"Topology: {shape_name}")
        self.topo_reason_lbl.config(text=reasoning_text)

        adjacency = spec.get("adjacency", {})
        agent_names = list(agents.keys())
        n = len(agent_names)

        if n == 0:
            return

        center_x, center_y = 160, 200
        radius = 95 if n > 2 else 60
        node_radius = 24

        for i, name in enumerate(agent_names):
            angle = (2 * math.pi * i) / n - (math.pi / 2)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[name] = (x, y)

        for src, targets in adjacency.items():
            if src not in self.node_positions:
                continue
            x1, y1 = self.node_positions[src]

            for dst in targets:
                if dst not in self.node_positions:
                    continue
                x2, y2 = self.node_positions[dst]

                angle = math.atan2(y2 - y1, x2 - x1)
                start_x = x1 + node_radius * math.cos(angle)
                start_y = y1 + node_radius * math.sin(angle)
                end_x = x2 - node_radius * math.cos(angle)
                end_y = y2 - node_radius * math.sin(angle)

                self.graph_canvas.create_line(
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    arrow=tk.LAST,
                    arrowshape=(9, 11, 4),
                    fill="#7F8C8D",
                    width=2,
                )

        for name in agent_names:
            x, y = self.node_positions[name]
            bg_color, accent_color = self._get_agent_style(name)

            circle = self.graph_canvas.create_oval(
                x - node_radius,
                y - node_radius,
                x + node_radius,
                y + node_radius,
                fill=bg_color,
                outline=accent_color,
                width=3,
            )
            self.node_items[name] = (circle, bg_color, accent_color)

            display_name = name[:9] + ".." if len(name) > 11 else name
            self.graph_canvas.create_text(
                x,
                y,
                text=display_name,
                font=("Segoe UI", 8, "bold"),
                fill="#2C3E50",
            )

            role_text = ""
            if name == spec.get("entry_agent"):
                role_text += "[ENTRY]"
            if name == spec.get("output_agent"):
                role_text += " [OUT]" if role_text else "[OUT]"

            if role_text:
                self.graph_canvas.create_text(
                    x,
                    y + node_radius + 10,
                    text=role_text,
                    font=("Segoe UI", 7, "bold"),
                    fill="#E65100" if "ENTRY" in role_text else "#2E7D32",
                )

    def highlight_active_node(self, agent_id: str):
        if agent_id in self.node_items:
            circle, bg_color, accent_color = self.node_items[agent_id]
            self.graph_canvas.itemconfig(
                circle, fill="#FFEB3B", outline="#F57F17", width=4
            )
            self.after(
                600,
                lambda: self.graph_canvas.itemconfig(
                    circle, fill=bg_color, outline=accent_color, width=3
                ),
            )

    def add_chat_bubble(self, sender: str, message: str, is_memory: bool = False):
        bg_color, accent_color = self._get_agent_style(sender)

        # Auto-detect canary or payload signature to trigger red ring
        if (
            "EVIL-MALWARE" in message
            or "SYSTEM NOTICE:" in message
            or "ZEBRA-" in message
        ):
            self.mark_node_infected(sender)

        self.highlight_active_node(sender)

        wrapper = tk.Frame(self.scrollable_frame, bg="#F4F6F8", pady=4)
        wrapper.pack(fill=tk.X, expand=True, padx=5)

        card_bg = "#FFEBEE" if sender in self.infected_nodes and not is_memory else ("#E0E0E0" if is_memory else bg_color)
        border_color = "#D32F2F" if sender in self.infected_nodes and not is_memory else ("#999999" if is_memory else accent_color)

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
        if sender in self.infected_nodes and not is_memory:
            label_title += " ⚠️ INFECTED"

        title_lbl = tk.Label(
            card,
            text=label_title,
            font=("Segoe UI", 9, "bold"),
            fg="#D32F2F" if sender in self.infected_nodes else ("#555555" if is_memory else accent_color),
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
            wraplength=480,
            anchor="w",
        )
        body_lbl.pack(fill=tk.X, pady=(4, 0))

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def set_final_answer(self, final_text: str):
        """Displays full final answer in bottom box and automatically copies to system clipboard."""
        if not final_text:
            return

        self.final_answer_text.config(state=tk.NORMAL)
        self.final_answer_text.delete("1.0", tk.END)
        self.final_answer_text.insert("1.0", final_text)
        self.final_answer_text.see("1.0")
        self.final_answer_text.config(state=tk.DISABLED)

        # Auto-copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(final_text)
        self.update()


def run_system_with_ui(spec, agents, task, ui: AgentChatUI):
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

            output, is_final = agent.update_state(messages)
            memory_note = agent.memory_log[-1] if agent.memory_log else ""

            if memory_note:
                ui.after(0, ui.add_chat_bubble, agent_id, memory_note, True)
            ui.after(0, ui.add_chat_bubble, agent_id, output, False)

            if agent_id == spec["output_agent"]:
                last_output = output
                if is_final:
                    print("Final output reached by output agent.")
                    ui.after(0, ui.set_final_answer, last_output)
                    return last_output

            for target in adjacency.get(agent_id, []):
                outgoing.append((target, output))

        for target, message in outgoing:
            inbox[target].append(message)

        if not any(inbox.values()):
            break

    if last_output:
        ui.after(0, ui.set_final_answer, last_output)
    return last_output


def main():
    task = input("Task: ")
    security = input("Security level (1-10): ").strip()

    spec, agents, task = get_agent_job_summaries(task, security)
    print("\nAdjacency list:", spec["adjacency"])
    print("Entry:", spec["entry_agent"], "| Output:", spec["output_agent"])

    ui = AgentChatUI(title=f"Multi-Agent Chat - {task[:30]}...")
    ui.draw_topology(spec, agents)

    def background_runner():
        final = run_system_with_ui(spec, agents, task, ui)
        print("\nFINAL ANSWER:", final)

    thread = threading.Thread(target=background_runner, daemon=True)
    thread.start()

    ui.mainloop()


if __name__ == "__main__":
    main()