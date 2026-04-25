from utils.llm import call_llm

def risk_agent(state: dict) -> dict:
    context = state.get("context", "")
    question = state.get("question", "")

    prompt = f"""You are a legal risk analyst reviewing a contract.

User question: {question}

Relevant contract clauses:
{context}

Assess the legal and financial risk of the clauses relevant to the question above.
Consider: liability exposure, one-sided terms, missing protections, penalty clauses, 
irrevocable rights, unlimited damages, or unfair obligations.

Respond in this exact format:
RISK_LEVEL: [low/medium/high]
REASONING: [2-3 sentences explaining why, based on the actual text above]

Your assessment:"""

    response = call_llm(prompt)

    risk_level = "medium"
    reasoning = response

    for line in response.splitlines():
        line_lower = line.lower()
        if line_lower.startswith("risk_level:"):
            val = line.split(":", 1)[-1].strip().lower()
            if val in ("low", "medium", "high"):
                risk_level = val
        elif line_lower.startswith("reasoning:"):
            reasoning = line.split(":", 1)[-1].strip()

    state["risk_score"] = risk_level
    state["risk_reasons"] = [reasoning]
    return state