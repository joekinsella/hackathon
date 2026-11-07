import json

import detail_job



def main() -> list[str]:
    """Prompts for input, executes the agent assignment request, and returns a list of job summaries."""
    task = input("Enter a task for an AI agent system: ").strip()
    if not task:
        print("Task cannot be empty.")
        return []

    print("\nGenerating sub-agent roles...")
    jobs = detail_job.get_agent_job_summaries(task)

    # Transform structured jobs into a list of summary strings
    summaries = [f"{job['title']}: {job['summary']}" for job in jobs]

    # Print output
    print(f"\n--- Assigned Jobs ({len(summaries)}) ---")
    for idx, summary in enumerate(summaries, 1):
        print(f"{idx}. {summary}")

    # Return list of summaries
    return summaries


if __name__ == "__main__":
    job_summaries_list = main()