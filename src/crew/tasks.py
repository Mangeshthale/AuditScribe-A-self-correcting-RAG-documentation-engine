# src/crew/tasks.py
from crewai import Task


def get_verification_tasks(raw_answer, critic_agent, writer_agent):
    """
    Critic: validates facts silently and outputs only verified content.
    Writer: formats that verified content into clean Markdown.
    Question is NOT passed — Writer's job is formatting only, not re-answering.
    """

    # Critic outputs clean verified facts — no headers, no conclusions, no meta-commentary
    validation_task = Task(
        description=(
            f"Review the following answer for factual accuracy:\n\n"
            f"--- ANSWER ---\n{raw_answer}\n--------------\n\n"
            "Output ONLY the verified factual content from this answer. "
            "Silently correct any errors you find. "
            "Do NOT write headers, section titles, 'Conclusion', 'Summary', "
            "or any meta-commentary about the review process. "
            "Do NOT add information that was not in the original answer. "
            "If there is a single factual error that cannot be corrected, "
            "add one short note at the end: 'Note: [issue]'."
        ),
        expected_output=(
            "The verified factual content only — plain prose or bullet points. "
            "No headers. No 'Conclusion'. No analysis commentary."
        ),
        agent=critic_agent
    )

    # Writer formats the verified content — does not re-answer, does not add new info
    formatting_task = Task(
        description=(
            "Take the verified content from the previous step and format it "
            "into clean, readable Markdown. "
            "Use bullet points or short paragraphs as appropriate. "
            "Do NOT add new information, do NOT re-analyse, do NOT add a Conclusion section. "
            "Your only job is presentation — make it easy to read."
        ),
        expected_output=(
            "The same verified content formatted in clean Markdown. "
            "No new information added. No Conclusion section."
        ),
        agent=writer_agent,
        context=[validation_task]
    )

    return [validation_task, formatting_task]
