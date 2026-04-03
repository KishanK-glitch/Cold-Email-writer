import os
from langchain_groq import ChatGroq
from backend.models import AgentState, CompanyDNA


# ─── Prompts ─────────────────────────────────────────────────────────────────

STRATEGIST_SYSTEM_PROMPT = (
    "You are a ruthless sales strategist. \n\n"
    "Inputs provided:\n"
    "1. Company DNA (Value prop, target audience, recent news).\n"
    "2. The User's Offering.\n\n"
    "Your objective: Write a single, highly specific, one-sentence \"Hook\". \n"
    "The hook must connect ONE specific pain point or recent initiative from the Company DNA directly to the User's Offering.\n\n"
    "STRICT CONSTRAINTS:\n"
    "- Output ONLY the raw text of the single-sentence hook. \n"
    "- DO NOT output any conversational filler. \n"
    "- DO NOT say \"Here is a hook\" or \"Hook:\". \n"
    "- Keep it under 20 words. No buzzwords."
)

COPYWRITER_SYSTEM_PROMPT = (
    "You are a founder writing a quick text-like email to another busy executive. \n"
    "Your writing is ruthlessly concise, casual, and direct. You write exactly like the examples provided.\n\n"
    "Inputs provided:\n"
    "1. The Target Company URL.\n"
    "2. The Strategic Hook (The reason you are reaching out).\n\n"
    "Your objective: Write a Subject Line and a 3-sentence cold email based on the hook.\n\n"
    "STRICT CONSTRAINTS:\n"
    "1. Banned Words: leverage, amplify, synergy, seamless, cutting-edge, innovative, delve, unlock, elevate, streamline, comprehensive.\n"
    '2. Banned Phrases: "I hope this finds you well", "My name is", "I am reaching out because", "I would love to".\n'
    "3. Structure: \n"
    "   - Sentence 1: The Observation (Based strictly on the hook).\n"
    "   - Sentence 2: The Value (What you do/The offering).\n"
    "   - Sentence 3: The Soft CTA (A low-friction question).\n"
    "4. Tone: 8th-grade reading level. Start the email immediately without a \"Hi [Name]\" if possible. \n"
    '5. Output format: You must include "Subject: [your subject]" at the top. Use all-lowercase for the subject line.\n\n'
    "EXAMPLES OF PERFECT OUTPUT:\n\n"
    "Subject: your recent launch\n"
    "Saw the news about the recent product launch. Looks solid.\n"
    "We built a system that automates the backend lead routing for launches like this so sales doesn't drop the ball.\n"
    "Worth a quick chat to see if it fits your current stack?\n"
    "Best,\n"
    "Kishan\n\n"
    "Subject: scaling outbound\n"
    "Noticed you're ramping up outbound efforts this quarter.\n"
    "I build custom AI agents that handle the initial research and drafting, usually cutting rep time by about 60%.\n"
    "Are you currently exploring anything like this?\n"
    "Cheers,\n"
    "Kishan\n"
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _require_groq_key() -> str:
    """Raise a descriptive error at call-time (not import-time) if the key is absent."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it to your Railway service variables before deploying."
        )
    return key


def get_llm() -> ChatGroq:
    _require_groq_key()
    return ChatGroq(model="llama-3.3-70b-versatile")


# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def researcher_node(state: AgentState) -> dict:
    content = state.get("scraped_content", "")
    if not content:
        return {"error": "No scraped content available."}

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(CompanyDNA)
        prompt = (
            "\n    Analyze the following website content and extract the Company DNA.\n"
            "    Noise should be ignored. Focus on:\n"
            "    1. Value Proposition\n"
            "    2. Target Audience\n"
            "    3. Recent News / Updates / Key Features\n\n"
            "    Website Content:\n    "
            + content
            + "\n    "
        )
        dna = structured_llm.invoke(prompt)
        return {"company_dna": dna}
    except Exception as e:
        return {"error": f"Failed to extract Company DNA: {str(e)}"}


def strategist_node(state: AgentState) -> dict:
    dna = state.get("company_dna")
    offering = state.get("user_offering", "")
    if not dna or not offering:
        return {"error": "Missing Company DNA or User Offering."}

    try:
        llm = get_llm()
        prompt = (
            STRATEGIST_SYSTEM_PROMPT
            + "\n\n---\nClient's Offering: "
            + offering
            + "\n\nTarget Company DNA:\n- Value Proposition: "
            + dna.value_proposition
            + "\n- Target Audience: "
            + dna.target_audience
            + "\n- Recent News/Updates: "
            + dna.recent_news
            + "\n"
        )
        response = llm.invoke(prompt)
        return {"hook": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Hook: {str(e)}"}


def copywriter_node(state: AgentState) -> dict:
    hook = state.get("hook", "")
    url = state.get("url", "")
    if not hook:
        return {"error": "Missing Hook."}

    try:
        llm = get_llm()
        prompt = (
            COPYWRITER_SYSTEM_PROMPT
            + "\n\n---\nTarget Company URL: "
            + url
            + "\nStrategic Hook: "
            + hook
            + "\n"
        )
        response = llm.invoke(prompt)
        return {"email": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Email: {str(e)}"}
