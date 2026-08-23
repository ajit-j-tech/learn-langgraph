from __future__ import annotations
from typing import TypedDict, Literal
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END

from langchain_openai import ChatOpenAI

# Create the LLM
llm = ChatOpenAI(model="gpt-5.6-terra", temperature=0)

MAX_ITERATIONS = 5
AGENTS = Literal["researcher", "analyst", "verifier", "FINISH"]

# Create State for Supervisor Pattern
class WorkflowState(TypedDict):
    question: str                               # User Question
    findings: list[dict]                        # Findings or Facts wiht information and source associated with it
    verification: str                           # Verification flag for each fact above
    analysis: str                               # Detailed Analysis of the information fetched with facts
    next_agent: Literal["researcher", "analyst", "verifier", "FINISH"]
    iteration: int = 0
    final_answer: str
    task: str

# Define the output schemas for LLMs
class Finding(BaseModel):
    claim: str
    source: str
    confidence: Literal["LOW", "MEDIUM", "HIGH"]

class ResearchResult(BaseModel):
    findings: list[Finding]

class AnalysisResult(BaseModel):
    analysis: str

class VerificationResult(BaseModel):
    verification: str
    known_gaps: list[str]

class DecisionRouter(BaseModel):
    next_agent: AGENTS = "researcher"
    task: str = Field(description="A focused task for next agent")

# Create the Agent Ndes
def researcher(state: WorkflowState) -> dict:
    """
    This node/agent researches via LLM and find the sources
    and returns a structured output
    """
    question = state.get("question")
    task = state.get("task", "")

    question_prompt = f"""You are an experienced research specialist.
        Your Task: {task}
        Research Question: {question}
        Return upto 3 concise findings. Every finding must be supported by source and your confidence.
        DO NOT draft any summary or final output. If you cant support any claim, omit it.
    """

    result = llm.with_structured_output(ResearchResult).invoke(question_prompt)

    return {
        "findings": [finding.model_dump() for finding in result.findings]
    }

def analyst(state: WorkflowState) -> dict:
    """
    This node/agent analyses the findings into a detailed summary
    """
    question = state.get("question")
    findings = state.get("findings")
    task = state.get("task", "")

    prompt = f"""You are an experienced analyst.
        Analyse all the findings and create a detailed summary.
        Synthesise only supplied findings, state uncertainty where evidence is weak.
        Question: {question}
        Findings: {findings}
        Your Task: {task}
    """
    result = llm.with_structured_output(AnalysisResult).invoke(prompt)

    return {
        "analysis": result.analysis
    }

def verifier(state: WorkflowState) -> dict:
    """
    This node/agent vertifies the findings and analysis.
    """
    question = state.get("question")
    findings = state.get("findings")
    analysis = state.get("analysis")
    task = state.get("task", "")

    prompt = f"""
        You are an experienced auditor of research papers and content.
        Question: {question}
        Findings: {findings}
        Analysis: {analysis}
        Your Task: {task}
        Identify unsupported claims, missing sources, or unresolved conflicts. Do not add facts.
    """
    result = llm.with_structured_output(VerificationResult).invoke(prompt)

    return result.model_dump()

# Define the Supervisor Agent
def supervisor(state: WorkflowState):
    """This is supervisor node/agent"""
    prompt = f"""You are the supervisor of a bounded research graph.
        Question: {state['question']}
        Findings: {state.get('findings', [])}
        Analysis: {state.get('analysis', '')}
        Verification: {state.get('verification', '')}

        Return that exact next agent and a concise task. Do not invent agents.
    """
    iteration = state.get("iteration", 0) + 1
    if iteration >= MAX_ITERATIONS:
        return {
            "next_agent": "FINISH",
            "iteration": iteration
        }
    result = llm.with_structured_output(DecisionRouter).invoke(prompt)

    return {
        "next_agent": result.next_agent,
        "task": result.task,
        "iteration": iteration
    }

def finalize(state: WorkflowState) -> dict:
    citations = "\n".join(f"- {finding['source']}" for finding in state.get("findings", []))
    gaps = "; ".join(state.get("known_gaps", [])) or "None"
    return {
        "final_answer": (
            f"{state.get('analysis', 'No analysis was produced.')}\n\n"
            f"Verification: {state.get('verification', 'Not performed.')}\n"
            f"Known gaps: {gaps}\n\nSources:\n{citations}"
        )
    }

# Simple logic for routing flow to appropriate node/agent
def route_supervisor(state: WorkflowState):
    return state.get("next_agent", "FINISH")

# Create the Graph for Worflow
graph_builder = StateGraph(WorkflowState)

# Add the nodes : Please note that we are using Agent as nods for learning purpose
graph_builder.add_node("supervisor", supervisor)
graph_builder.add_node("researcher", researcher)
graph_builder.add_node("analyst", analyst)
graph_builder.add_node("verifier", verifier)
graph_builder.add_node("finalize", finalize)

# Create the edges
graph_builder.add_edge(START, "supervisor")
graph_builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "researcher": "researcher",
        "analyst": "analyst",
        "verifier": "verifier",
        "FINISH": "finalize"
    }
)
graph_builder.add_edge("researcher", "supervisor")
graph_builder.add_edge("analyst", "supervisor")
graph_builder.add_edge("verifier", "supervisor")
graph_builder.add_edge("finalize", END)

# Compile the graph
graph = graph_builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "question": "How should a LangGraph multi-agent system coordinate research?"
    })
    print(result)
