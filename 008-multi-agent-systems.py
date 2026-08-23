from __future__ import annotations

import os
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - supports reading without dependencies
    ChatOpenAI = None  # type: ignore[assignment,misc]


MODEL_NAME = "gpt-5.6-terra"
MAX_ITERATIONS = 4
AgentName = Literal["researcher", "analyst", "verifier", "FINISH"]


class RouteDecision(BaseModel):
    next_agent: AgentName
    task: str = Field(description="A focused task for the next agent")


class Finding(BaseModel):
    claim: str
    source: str
    confidence: Literal["low", "medium", "high"]


class ResearchResult(BaseModel):
    findings: list[Finding]


class AnalysisResult(BaseModel):
    analysis: str


class VerificationResult(BaseModel):
    verification: str
    known_gaps: list[str]


class ResearchState(TypedDict):
    question: str
    findings: NotRequired[list[dict]]
    analysis: NotRequired[str]
    verification: NotRequired[str]
    known_gaps: NotRequired[list[str]]
    next_agent: NotRequired[AgentName]
    iteration: NotRequired[int]
    final_answer: NotRequired[str]
    model_errors: NotRequired[list[str]]


def get_llm(reasoning_effort: Literal["low", "medium"]):
    if ChatOpenAI is None or not os.getenv("OPENAI_API_KEY"):
        return None
    return ChatOpenAI(model=MODEL_NAME, reasoning_effort=reasoning_effort)


def fallback_route(state: ResearchState) -> RouteDecision:
    if not state.get("findings"):
        return RouteDecision(next_agent="researcher", task="Collect source-backed findings.")
    if not state.get("analysis"):
        return RouteDecision(next_agent="analyst", task="Synthesize the collected findings.")
    if not state.get("verification"):
        return RouteDecision(next_agent="verifier", task="Verify findings and analysis.")
    return RouteDecision(next_agent="FINISH", task="All required work is complete.")


def supervisor(state: ResearchState) -> dict:
    """Use the LLM for routing, then enforce the graph's allowed transition."""
    iteration = state.get("iteration", 0) + 1
    if iteration >= MAX_ITERATIONS:
        return {"iteration": iteration, "next_agent": "FINISH"}

    fallback = fallback_route(state)
    llm = get_llm("medium")
    if llm is None:
        return {"iteration": iteration, "next_agent": fallback.next_agent}

    prompt = f"""You are the supervisor of a bounded research graph.
Question: {state['question']}
Findings: {state.get('findings', [])}
Analysis: {state.get('analysis', '')}
Verification: {state.get('verification', '')}

The only valid next step for this graph state is {fallback.next_agent}.
Return that exact next agent and a concise task. Do not invent agents."""

    try:
        decision = llm.with_structured_output(RouteDecision).invoke(prompt)
        next_agent = decision.next_agent if decision.next_agent == fallback.next_agent else fallback.next_agent
        return {"iteration": iteration, "next_agent": next_agent}
    except Exception as error:  # Keep the learning graph runnable without live access.
        return {
            "iteration": iteration,
            "next_agent": fallback.next_agent,
            "model_errors": [f"Supervisor fallback: {error}"],
        }


def researcher(state: ResearchState) -> dict:
    llm = get_llm("low")
    if llm is None:
        return {
            "findings": [
                {
                    "claim": "LangGraph represents agent workflows as explicit state, nodes, and edges.",
                    "source": "https://langchain-ai.github.io/langgraph/",
                    "confidence": "high",
                }
            ]
        }

    prompt = f"""You are a research specialist.
Research question: {state['question']}
Return up to three concise findings. Every finding needs a source URL and confidence.
Do not draft the final answer. If you cannot support a claim, omit it."""
    try:
        result = llm.with_structured_output(ResearchResult).invoke(prompt)
        return {"findings": [finding.model_dump() for finding in result.findings]}
    except Exception as error:
        return {"findings": [], "model_errors": [f"Researcher failed: {error}"]}


def analyst(state: ResearchState) -> dict:
    llm = get_llm("low")
    if llm is None:
        claims = " ".join(finding["claim"] for finding in state.get("findings", []))
        return {"analysis": f"The available evidence supports explicit graph state and routing. {claims}"}

    prompt = f"""You are an analysis specialist.
Question: {state['question']}
Findings: {state.get('findings', [])}
Synthesize only the supplied findings. State uncertainty where evidence is weak."""
    try:
        result = llm.with_structured_output(AnalysisResult).invoke(prompt)
        return {"analysis": result.analysis}
    except Exception as error:
        return {"analysis": "Analysis unavailable.", "model_errors": [f"Analyst failed: {error}"]}


def verifier(state: ResearchState) -> dict:
    llm = get_llm("low")
    if llm is None:
        gaps = [finding["claim"] for finding in state.get("findings", []) if not finding.get("source")]
        status = "passed" if not gaps else "failed: findings without sources"
        return {"verification": f"Verification {status}.", "known_gaps": gaps}

    prompt = f"""You are a verification specialist.
Question: {state['question']}
Findings: {state.get('findings', [])}
Analysis: {state.get('analysis', '')}
Identify unsupported claims, missing sources, or unresolved conflicts. Do not add facts."""
    try:
        result = llm.with_structured_output(VerificationResult).invoke(prompt)
        return result.model_dump()
    except Exception as error:
        return {
            "verification": "Verification unavailable.",
            "known_gaps": ["The verifier did not complete."],
            "model_errors": [f"Verifier failed: {error}"],
        }


def finalize(state: ResearchState) -> dict:
    citations = "\n".join(f"- {finding['source']}" for finding in state.get("findings", []))
    gaps = "; ".join(state.get("known_gaps", [])) or "None"
    return {
        "final_answer": (
            f"{state.get('analysis', 'No analysis was produced.')}\n\n"
            f"Verification: {state.get('verification', 'Not performed.')}\n"
            f"Known gaps: {gaps}\n\nSources:\n{citations}"
        )
    }


def route_supervisor(state: ResearchState) -> AgentName:
    return state.get("next_agent", "FINISH")


builder = StateGraph(ResearchState)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher)
builder.add_node("analyst", analyst)
builder.add_node("verifier", verifier)
builder.add_node("finalize", finalize)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {"researcher": "researcher", "analyst": "analyst", "verifier": "verifier", "FINISH": "finalize"},
)
builder.add_edge("researcher", "supervisor")
builder.add_edge("analyst", "supervisor")
builder.add_edge("verifier", "supervisor")
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {"question": "How should a LangGraph multi-agent system coordinate research?"}
    )
    print(result["final_answer"])
