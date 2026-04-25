from utils.llm import call_llm

def explanation_agent(state: dict) -> dict:
    question = state.get("question", "")
    context = state.get("context", "")
    risk_score = state.get("risk_score", "unknown")
    risk_reasons = state.get("risk_reasons", [])
    clause_types = state.get("clause_types", [])
    passed = state.get("compliance_passed", [])
    failed = state.get("compliance_failed", [])
    chunks = state.get("retrieved_chunks", [])

    prompt = f"""You are a contract analyst assistant.
Answer the user's question clearly and concisely based only on the contract text provided.

User Question: {question}

Relevant Contract Text:
{context}

Instructions:
- Answer the question directly using information from the contract text
- Quote relevant parts where helpful
- Be concise (3-5 sentences max)
- Do not make up information not present in the text

Answer:"""

    direct_answer = call_llm(prompt)

    source_preview = chunks[0][:300] if chunks else "No source text available."

    final_answer = f"""QUESTION
{question}

DIRECT ANSWER
{direct_answer}

RISK ASSESSMENT
Level    : {risk_score.upper()}
Reasoning: {risk_reasons[0] if risk_reasons else 'N/A'}

IDENTIFIED CLAUSES
{', '.join(clause_types) if clause_types else 'None identified'}

COMPLIANCE
Passed : {', '.join(passed) if passed else 'None'}
Failed : {', '.join(failed) if failed else 'None'}

SOURCE EXCERPT
{source_preview}...
"""

    state["final_answer"] = final_answer.strip()
    return state