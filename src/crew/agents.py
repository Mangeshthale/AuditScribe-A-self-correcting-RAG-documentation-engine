# src/crew/agents.py
import os
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Crew, LLM
from .tasks import get_verification_tasks

# Removed unused imports: ChatGroq (not needed, crewai uses its own LLM wrapper), Process

groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3  # lowered from 0.5 — less creative drift = more faithful output
)

critic = Agent(
    role='Senior Technical Auditor',
    goal='Verify technical accuracy. Flag hallucinations. Be brief.',
    backstory='A veteran engineer who values precision over verbosity.',
    llm=groq_llm,
    max_rpm=10,
    verbose=False  # changed to False — reduces terminal noise, speeds up slightly
)

writer = Agent(
    role='Technical Writer',
    goal='Rewrite the validated answer clearly and concisely in Markdown.',
    backstory='Expert at turning technical reviews into clean documentation.',
    llm=groq_llm,
    max_rpm=15,
    verbose=False  # changed to False
)


def run_verification_crew(raw_answer):
    tasks = get_verification_tasks(raw_answer, critic, writer)
    crew = Crew(agents=[critic, writer], tasks=tasks, verbose=False)
    return crew.kickoff()
