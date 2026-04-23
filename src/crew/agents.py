import os
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Crew, LLM
from .tasks import get_verification_tasks

critic_llm = LLM(
    model="groq/qwen/qwen3-32b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1  
)

writer_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0  
)

critic = Agent(
    role='Senior Technical Auditor',
    goal='Verify technical accuracy. Flag hallucinations. Be brief.',
    backstory='A veteran engineer who values precision over verbosity.',
    llm=critic_llm,
    max_rpm=10,
    verbose=False
)

writer = Agent(
    role='Technical Writer',
    goal='Rewrite the validated answer clearly and concisely in Markdown.',
    backstory='Expert at turning technical reviews into clean documentation.',
    llm=writer_llm,
    max_rpm=15,
    verbose=False 
)

def run_verification_crew(raw_answer):
    tasks = get_verification_tasks(raw_answer, critic, writer)
    crew = Crew(agents=[critic, writer], tasks=tasks, verbose=False)
    return crew.kickoff()
