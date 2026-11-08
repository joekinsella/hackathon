#runner code
def run_system(spec, agents, task):
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

            if agent_id == spec["output_agent"]:
                last_output = output
                if is_final:
                    print("Final output reached by the output agent.")
                    return output

            # FIX: Use .get() to avoid KeyError
            for target in adjacency.get(agent_id, []):
                outgoing.append((target, output))

        for target, message in outgoing:
            inbox[target].append(message)

        if not any(inbox.values()):
            break

    return last_output