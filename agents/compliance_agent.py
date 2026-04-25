from utils.llm import call_llm

REQUIRED_CLAUSES = [
    {"name": "Payment Terms",      "keywords": ["payment", "invoice", "fee", "due"]},
    {"name": "Termination Clause", "keywords": ["termination", "terminate"]},
    {"name": "Confidentiality",    "keywords": ["confidential", "non-disclosure"]},
    {"name": "Governing Law",      "keywords": ["governing law", "jurisdiction"]},
    {"name": "Liability Limitation","keywords": ["liability", "liable"]},
    {"name": "Dispute Resolution", "keywords": ["dispute", "arbitration", "mediation"]},
]

def compliance_agent(state: dict) -> dict:
    # Check against retrieved context only (not full contract)
    context = state.get("context", "").lower()
    passed = []
    failed = []

    for rule in REQUIRED_CLAUSES:
        if any(kw in context for kw in rule["keywords"]):
            passed.append(rule["name"])
        else:
            failed.append(rule["name"])

    state["compliance_passed"] = passed
    state["compliance_failed"] = failed
    return state