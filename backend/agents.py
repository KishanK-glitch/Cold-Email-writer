import os
from langchain_groq import ChatGroq
from backend.models import AgentState, CompanyDNA

# ─── Prompts ─────────────────────────────────────────────────────────────────

INTENT_SYSTEM_PROMPT = (
    "You are an expert intent classifier. Analyze the user's offering/request below. "
    "Classify it into exactly ONE of the following three categories:\n"
    "1. 'sales' - The user is selling a product, software, or service to the company.\n"
    "2. 'partnership' - The user wants to collaborate, integrate, or co-market.\n"
    "3. 'grant' - The user is asking for funding, a grant, sponsorship, or financial support.\n\n"
    "STRICT CONSTRAINT: Output ONLY the single word ('sales', 'partnership', or 'grant') in lowercase. No punctuation, no explanation."
)

BASE_WRITER_RULES = (
    "STRICT CONSTRAINTS:\n"
    "1. Banned Words: leverage, amplify, synergy, seamless, cutting-edge, innovative, delve, unlock, elevate, streamline.\n"
    '2. Banned Phrases: "I hope this finds you well", "My name is", "I am reaching out because".\n'
    "3. Tone: 8th-grade reading level. Ruthlessly concise and direct.\n"
    '4. Output format: Include "Subject: [your subject]" at the top in all-lowercase. No conversational filler before or after the email.\n'
)

SALES_WRITER_PROMPT = (
    "You are a founder writing a B2B sales cold email to an executive.\n"
    "Inputs provided:\n"
    "1. Company DNA (Value prop, target audience, recent news).\n"
    "2. The User's Offering.\n\n"
    "Your objective: Write a Subject Line and a 3-sentence email.\n"
    "Sentence 1: An observation tying a specific detail from their Company DNA to a pain point.\n"
    "Sentence 2: The Value (Pitching the User's Offering as the exact solution).\n"
    "Sentence 3: A low-friction soft CTA (e.g., 'Worth a chat?').\n\n"
    + BASE_WRITER_RULES
)

PARTNERSHIP_WRITER_PROMPT = (
    "You are a founder writing to another founder proposing a strategic partnership or integration.\n"
    "Inputs provided:\n"
    "1. Company DNA (Value prop, target audience, recent news).\n"
    "2. The User's Offering.\n\n"
    "Your objective: Write a Subject Line and a 3-sentence email.\n"
    "Sentence 1: Acknowledge their specific market position or recent news from their DNA.\n"
    "Sentence 2: Propose how integrating/partnering with the User's Offering creates mutual value for both user bases.\n"
    "Sentence 3: A low-friction soft CTA (e.g., 'Open to exploring an integration?').\n\n"
    + BASE_WRITER_RULES
)

GRANT_WRITER_PROMPT = (
    "You are a builder applying for a grant or funding from a Web3 foundation or company.\n"
    "Inputs provided:\n"
    "1. Company DNA (Value prop, target audience, recent news).\n"
    "2. The User's Project/Offering.\n\n"
    "Your objective: Write a Subject Line and a 3-sentence email.\n"
    "Sentence 1: Acknowledge their specific grant program, validator business, or ecosystem goals from their DNA.\n"
    "Sentence 2: Explain how the User's Project specifically accelerates their ecosystem or solves a gap for them.\n"
    "Sentence 3: A direct CTA asking for the next step in their grant/funding process.\n\n"
    + BASE_WRITER_RULES
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _require_groq_key() -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it to your Railway service variables before deploying."
        )
    return key


def get_llm() -> ChatGroq:
    _require_groq_key()
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)


# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def researcher_node(state: AgentState) -> dict:
    content = state.get("scraped_content", "")
    if not content:
        return {"error": "No scraped content available."}

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(CompanyDNA)
        prompt = (
            "\nAnalyze the following website content and extract the Company DNA.\n"
            "Noise should be ignored. Focus on:\n"
            "1. Value Proposition\n"
            "2. Target Audience\n"
            "3. Recent News / Updates / Key Features\n\n"
            "Website Content:\n" + content + "\n"
        )
        dna = structured_llm.invoke(prompt)
        return {"company_dna": dna}
    except Exception as e:
        return {"error": f"Failed to extract Company DNA: {str(e)}"}


def intent_classifier_node(state: AgentState) -> dict:
    offering = state.get("user_offering", "")
    if not offering:
        return {"user_intent": "sales"} # Default fallback

    try:
        llm = get_llm()
        prompt = f"{INTENT_SYSTEM_PROMPT}\n\nUser Offering: {offering}"
        response = llm.invoke(prompt)
        intent = response.content.strip().lower()
        
        if intent not in ["sales", "partnership", "grant"]:
            intent = "sales" # Safety fallback
            
        return {"user_intent": intent}
    except Exception as e:
        return {"user_intent": "sales"}


def _execute_writer_node(state: AgentState, system_prompt: str) -> dict:
    dna = state.get("company_dna")
    offering = state.get("user_offering", "")
    url = state.get("url", "")
    
    if not dna or not offering:
        return {"error": "Missing Company DNA or User Offering."}

    try:
        llm = get_llm()
        prompt = (
            system_prompt
            + "\n\n---\nTarget Company URL: " + url
            + "\nClient's Offering/Request: " + offering
            + "\n\nTarget Company DNA:\n- Value Proposition: " + dna.value_proposition
            + "\n- Target Audience: " + dna.target_audience
            + "\n- Recent News/Updates: " + dna.recent_news
            + "\n"
        )
        response = llm.invoke(prompt)
        return {"email": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Email: {str(e)}"}


def sales_writer_node(state: AgentState) -> dict:
    return _execute_writer_node(state, SALES_WRITER_PROMPT)


def partnership_writer_node(state: AgentState) -> dict:
    return _execute_writer_node(state, PARTNERSHIP_WRITER_PROMPT)


def grant_writer_node(state: AgentState) -> dict:
    return _execute_writer_node(state, GRANT_WRITER_PROMPT)