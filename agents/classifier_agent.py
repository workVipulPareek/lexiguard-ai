from utils.llm import call_llm

def classifier_agent(state: dict) -> dict:
    context = state.get("context", "")
    question = state.get("question", "")

    prompt = f"""You are a legal contract analyst.
Given the following contract excerpt, identify the types of legal clauses present.

Question being analyzed: {question}

Contract excerpt:
{context}

List only the clause types that are actually present in the text above.
Respond with a comma-separated list only. Example: payment, termination, liability
Do not include clauses that are not mentioned in the text.

Clause types:"""

    response = call_llm(prompt)

    clauses = [
        c.strip().lower().replace(" ", "_")
        for c in response.split(",")
        if c.strip()
    ]

    state["clause_types"] = clauses if clauses else ["general"]
    return state