#runner code
def run_system(spec, agents, task):
    #spec is a dictionary with the format {"adjacency": adj_list{}, "roles": roles_desc{}, "entry_agent": Agent agnt1, "output_agent": Agent agnt2}
    adjacency = spec["adjacency"]
    inbox = {agent_id: [] for agent_id in agents}        # creates one mailbox[] per agent
    inbox[spec["entry_agent"]].append(task)    # user defined task goes to the entry agent
    last_output = None

    for round_num in range(len(agents)):
        print(f"\n--- round {round_num} --- inboxes: { {a: len(m) for a, m in inbox.items()} }")
        outgoing = []                                    # held until everyone has run

        for agent_id, agent in agents.items():
            if not inbox[agent_id]:                      # no mail -> skip
                continue

            messages = inbox[agent_id]
            inbox[agent_id] = []                         # empty the mailbox

            output = agent.update_state(messages)      #call update state with messages in agents inbox

            if agent_id == spec["output_agent"]:
                last_output = output
                

            for target in adjacency[agent_id]:           # update outgoing with tuple containing target_agent, message
                outgoing.append((target, output))
            

        for target, message in outgoing:                 # deliver from outgoing to inboxes of recieving agents
            inbox[target].append(message)

        if not any(inbox.values()):                      # nobody has mail -> done
            break

    return last_output
