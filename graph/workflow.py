from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.retriever_agent import retriever_agent
from agents.classifier_agent import classifier_agent
from agents.risk_agent import risk_agent
from agents.compliance_agent import compliance_agent
from agents.explanation_agent import explanation_agent


class ContractState(TypedDict):
    question: str
    file_path: str
    context: str
    retrieved_chunks: list
    clause_types: list
    risk_score: str
    risk_reasons: list
    compliance_passed: list
    compliance_failed: list
    final_answer: str


def build_workflow() -> StateGraph:
    graph = StateGraph(ContractState)

    graph.add_node("retriever", retriever_agent)
    graph.add_node("classifier", classifier_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("explanation", explanation_agent)

    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "classifier")
    graph.add_edge("classifier", "risk")
    graph.add_edge("risk", "compliance")
    graph.add_edge("compliance", "explanation")
    graph.add_edge("explanation", END)

    return graph.compile()


_workflow = None

def run_workflow(question: str, file_path: str) -> dict:
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()

    initial_state: ContractState = {
        "question": question,
        "file_path": file_path,
        "context": "",
        "retrieved_chunks": [],
        "clause_types": [],
        "risk_score": "",
        "risk_reasons": [],
        "compliance_passed": [],
        "compliance_failed": [],
        "final_answer": ""
    }

    result = _workflow.invoke(initial_state)

    return {
        "answer": result["final_answer"],
        "risk_score": result["risk_score"],
        "clause_types": result["clause_types"],
        "compliance_passed": result["compliance_passed"],
        "compliance_failed": result["compliance_failed"],
        "source_chunks": result["retrieved_chunks"]
    }