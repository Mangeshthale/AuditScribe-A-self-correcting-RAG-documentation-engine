# src/eval/evaluator.py
import asyncio
import sys

# nest_asyncio (used by ragas) can't patch uvloop.
# Force the standard asyncio event loop on all platforms.
if sys.platform != "win32":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
import time
import os
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from datasets import Dataset
from typing import Any, List, Optional
from agents.tools import get_embeddings


class GroqSafeLLM(ChatGroq):
    """Strips n>1 from every request — Groq only supports n=1."""

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs,
    ) -> ChatResult:
        kwargs.pop("n", None)
        kwargs["n"] = 1
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs,
    ) -> ChatResult:
        kwargs.pop("n", None)
        kwargs["n"] = 1
        return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
    
    def _get_invocation_params(self, **kwargs):
        params = super()._get_invocation_params(**kwargs)
        params.pop("n", None)
        params["n"] = 1
        return params


# Initialised once at module load — not per call
_groq_llm = LangchainLLMWrapper(
    GroqSafeLLM(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=2048
    )
)
_embeddings = LangchainEmbeddingsWrapper(get_embeddings())
_faithfulness_metric = Faithfulness(llm=_groq_llm)
_relevancy_metric = AnswerRelevancy(llm=_groq_llm, embeddings=_embeddings)


def run_evals(questions, answers, contexts):
    time.sleep(2)  # Groq free-tier RPM buffer

    safe_contexts = []
    for ctx in contexts:
        if isinstance(ctx, list) and len(ctx) > 0:
            safe_contexts.append([str(c) for c in ctx])
        else:
            safe_contexts.append(["No context retrieved."])

    dataset = Dataset.from_dict({
        "user_input": questions,
        "response": answers,
        "retrieved_contexts": safe_contexts,
    })

    results = evaluate(
        dataset,
        metrics=[_faithfulness_metric, _relevancy_metric],
    )

    def _scalar(val):
        if isinstance(val, list):
            return float(sum(val) / len(val)) if val else 0.0
        try:
            f = float(val)
            return 0.0 if f != f else f  # catch nan → 0.0
        except Exception:
            return 0.0

    return {
        "faithfulness": _scalar(results["faithfulness"]),
        "answer_relevancy": _scalar(results["answer_relevancy"]),
    }
