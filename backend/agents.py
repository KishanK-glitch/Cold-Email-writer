import os
from langchain_groq import ChatGroq
from backend.models import AgentState, CompanyDNA

STRATEGIST_SYSTEM_PROMPT = """You are a ruthless sales strategist. 

Inputs provided:
1. Company DNA (Value prop, target audience, recent news).
2. The User's Offering.

Your objective: Write a single, highly specific, one-sentence "Hook". 
The hook must connect ONE specific pain point or recent initiative from the Company DNA directly to the User's Offering.

STRICT CONSTRAINTS:
- Output ONLY the raw text of the single-sentence hook. 
- DO NOT output any conversational filler. 
- DO NOT say "Here is a hook" or "Hook:". 
- Keep it under 20 words. No buzzwords."""

COPYWRITER_SYSTEM_PROMPT = """You are a founder writing a quick text-like email to another busy executive. 
Your writing is ruthlessly concise, casual, and direct. You write exactly like the examples provided.

Inputs provided:
1. The Target Company URL.
2. The Strategic Hook (The reason you are reaching out).

Your objective: Write a Subject Line and a 3-sentence cold email based on the hook.

STRICT CONSTRAINTS:
1. Banned Words: leverage, amplify, synergy, seamless, cutting-edge, innovative, delve, unlock, elevate, streamline, comprehensive.
2. Banned Phrases: "I hope this finds you well", "My name is", "I am reaching out because", "I would love to".
3. Structure: 
   - Sentence 1: The Observation (Based strictly on the hook).
   - Sentence 2: The Value (What you do/The offering).
   - Sentence 3: The Soft CTA (A low-friction question).
4. Tone: 8th-grade reading level. Start the email immediately without a "Hi [Name]" if possible. 
5. Output format: You must include "Subject: [your subject]" at the top. Use all-lowercase for the subject line.

EXAMPLES OF PERFECT OUTPUT:

Subject: your recent launch
Saw the news about the recent product launch. Looks solid.
We built a system that automates the backend lead routing for launches like this so sales doesn't drop the ball.
Worth a quick chat to see if it fits your current stack?
Best,
Kishan

Subject: scaling outbound
Noticed you're ramping up outbound efforts this quarter.
I build custom AI agents that handle the initial research and drafting, usually cutting rep time by about 60%.
Are you currently exploring anything like this?
Cheers,
Kishan
"""

# FIX: Lowered temperature from 0.7 to 0.3 to force strict constraint adherence.
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3, 
        max_tokens=1024
    )

def researcher_node(state: AgentState):
    content = state.get("scraped_content", "")
    if not content:
        return {"error": "No scraped content available."}
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(CompanyDNA)
    
    prompt = f"""
    Analyze the following website content and extract the Company DNA.
    Noise should be ignored. Focus on:
    1. Value Proposition
    2. Target Audience
    3. Recent News / Updates / Key Features

    Website Content:
    {content}
    """
    
    try:
        dna = structured_llm.invoke(prompt)
        return {"company_dna": dna}
    except Exception as e:
        return {"error": f"Failed to extract Company DNA: {str(e)}"}


def strategist_node(state: AgentState):
    dna: CompanyDNA = state.get("company_dna")
    offering = state.get("user_offering", "")
    
    if not dna or not offering:
        return {"error": "Missing Company DNA or User Offering."}
    
    llm = get_llm()
    prompt = f"""{STRATEGIST_SYSTEM_PROMPT}

---
Client's Offering: {offering}

Target Company DNA:
- Value Proposition: {dna.value_proposition}
- Target Audience: {dna.target_audience}
- Recent News/Updates: {dna.recent_news}
"""
    
    try:
        response = llm.invoke(prompt)
        return {"hook": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Hook: {str(e)}"}


def copywriter_node(state: AgentState):
    hook = state.get("hook", "")
    url = state.get("url", "")
    
    if not hook:
        return {"error": "Missing Hook."}
    
    llm = get_llm()
    prompt = f"""{COPYWRITER_SYSTEM_PROMPT}

---
Target Company URL: {url}
Strategic Hook: {hook}
"""
    
    try:
        response = llm.invoke(prompt)
        return {"email": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Email: {str(e)}"}