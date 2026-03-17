import os
from langchain_groq import ChatGroq
from backend.models import AgentState, CompanyDNA

# Use llama-3.3-70b-versatile via Groq as requested
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024
    )

def researcher_node(state: AgentState):
    """
    Analyzes the scraped markdown and extracts the Company DNA.
    """
    content = state.get("scraped_content", "")
    if not content:
        return {"error": "No scraped content available."}
    
    llm = get_llm()
    # Structured output for Company DNA
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
    """
    Maps the user's offering to the specific pain points found by the Researcher.
    Identifies the 'Hook'.
    """
    dna: CompanyDNA = state.get("company_dna")
    offering = state.get("user_offering", "")
    
    if not dna or not offering:
        return {"error": "Missing Company DNA or User Offering."}
    
    llm = get_llm()
    prompt = f"""
    You are an expert sales strategist.
    
    Client's Offering: {offering}
    
    Target Company DNA:
    - Value Proposition: {dna.value_proposition}
    - Target Audience: {dna.target_audience}
    - Recent News/Updates: {dna.recent_news}
    
    Your task: Formulate a single, highly compelling 1-2 sentence "Hook" that directly connects the Client's Offering to the Target Company's specific context or recent news. The hook should identify a potential pain point or growth opportunity.
    """
    
    try:
        response = llm.invoke(prompt)
        return {"hook": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Hook: {str(e)}"}


def copywriter_node(state: AgentState):
    """
    Writes the final email based on the hook and constraints.
    """
    hook = state.get("hook", "")
    offering = state.get("user_offering", "")
    
    if not hook:
        return {"error": "Missing Hook."}
    
    llm = get_llm()
    prompt = f"""
    You are an elite B2B copywriter. Write a cold email using the following components:
    
    Client's Offering: {offering}
    Strategic Hook: {hook}
    
    STRICT CONSTRAINTS:
    1. No "I hope this finds you well" or any generic greetings.
    2. NO FLUFF.
    3. Maximum 3-4 sentences total.
    4. Must include a clear, low-friction Call to Action (CTA).
    5. Tone: Peer-to-peer, professional, not a bot.
    
    Output ONLY the email body (you can include a subject line at the top labeled "Subject: "). Nothing else.
    """
    
    try:
        response = llm.invoke(prompt)
        return {"email": response.content.strip()}
    except Exception as e:
        return {"error": f"Failed to generate Email: {str(e)}"}
