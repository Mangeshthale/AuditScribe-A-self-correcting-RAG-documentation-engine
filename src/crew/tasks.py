# src/crew/tasks.py
from crewai import Task

def get_verification_tasks(raw_answer, critic_agent, writer_agent):
    """
    Defines the specific sequence of work for the Sentinel Crew.
    """
    
    # 1. Fact-Checking Task
    validation_task = Task(
        description=(
            f"Carefully review the following technical answer for accuracy: \n\n"
            f"--- RAW ANSWER ---\n{raw_answer}\n-----------------\n\n"
            "Compare the content against known best practices. "
            "Identify any hallucinations, incorrect code syntax, or security risks. "
            "If the answer is correct, summarize the key technical merits."
        ),
        expected_output=(
            "A critical analysis report highlighting any errors found, "
            "or a confirmation that the technical logic is sound."
        ),
        agent=critic_agent
    )

    # 2. Documentation Formatting Task
    formatting_task = Task(
        description=(
            "Using ONLY the validated information from the previous step, "
            "write a concise technical answer. Do NOT add generic prerequisites "
            "or filler. Every sentence must directly answer the original question."
        ),
        expected_output=(
            "A complete, production-ready technical document in Markdown format "
            "that is easy for a developer to follow."
        ),
        agent=writer_agent,
        context=[validation_task]  # This ensures the writer waits for the critic
    )

    return [validation_task, formatting_task]