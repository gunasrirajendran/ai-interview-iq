from fastapi import APIRouter

router = APIRouter()

COMPANY_MODES = {
    "google": {
        "name": "Google",
        "focus": "system design, leadership, collaboration",
        "prompt": "Assess system design judgment, communication clarity, and ownership mindset."
    },
    "microsoft": {
        "name": "Microsoft",
        "focus": "customer obsession, execution, growth mindset",
        "prompt": "Assess customer impact, thoughtful tradeoffs, and collaborative delivery."
    },
    "amazon": {
        "name": "Amazon",
        "focus": "operational excellence, bias for action, customer obsession",
        "prompt": "Assess pragmatic problem solving, prioritization, and measurable impact."
    },
    "zoho": {
        "name": "Zoho",
        "focus": "product thinking, versatility, execution",
        "prompt": "Assess product instincts, scalability awareness, and ownership."
    },
    "tcs": {
        "name": "TCS",
        "focus": "delivery discipline, communication, adaptability",
        "prompt": "Assess structured thinking, reliability, and stakeholder communication."
    },
    "infosys": {
        "name": "Infosys",
        "focus": "consulting mindset, teamwork, delivery",
        "prompt": "Assess structured reasoning, client awareness, and collaborative execution."
    },
}


@router.get("/companies")
def list_company_modes():
    return [{"slug": slug, **meta} for slug, meta in COMPANY_MODES.items()]
