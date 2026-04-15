from langgraph.graph import StateGraph, END
from backend.models import AgentState
from backend.utils import scrape_url

# We will need to define these new nodes in agents.py next
from backend.agents import (
    researcher_node, 
    intent_classifier_node, 
    sales_writer_node, 
    partnership_writer_node, 
    grant_writer_node
)

def scrape_node(state: AgentState):
    url = state.get("url")
    try:
        content = scrape_url(url)
        return {"scraped_content": content}
    except Exception as e:
        return {"error": str(e)}

# ─── Routing Logic ──────────────────────────────────────────────────────────

def route_after_scrape(state: AgentState):
    if state.get("error"):
        return END
    return "researcher"

def route_after_researcher(state: AgentState):
    if state.get("error"):
        return END
    return "intent_classifier"

def route_after_intent(state: AgentState):
    """
    This is the core routing brain. It reads the intent classified by the LLM
    and directs the graph to the specialized writer.
    """
    if state.get("error"):
        return END
    
    intent = state.get("user_intent", "sales") # Default to sales if empty
    
    if intent == "partnership":
        return "partnership_writer"
    elif intent == "grant":
        return "grant_writer"
    else:
        return "sales_writer"

# ─── Build Graph ────────────────────────────────────────────────────────────

builder = StateGraph(AgentState)

# 1. Add all nodes
builder.add_node("scrape", scrape_node)
builder.add_node("researcher", researcher_node)
builder.add_node("intent_classifier", intent_classifier_node)
builder.add_node("sales_writer", sales_writer_node)
builder.add_node("partnership_writer", partnership_writer_node)
builder.add_node("grant_writer", grant_writer_node)

# 2. Set Entry
builder.set_entry_point("scrape")

# 3. Add Edges and Routing
builder.add_conditional_edges("scrape", route_after_scrape)
builder.add_conditional_edges("researcher", route_after_researcher)
builder.add_conditional_edges("intent_classifier", route_after_intent)

# All specialized writers terminate the graph
builder.add_edge("sales_writer", END)
builder.add_edge("partnership_writer", END)
builder.add_edge("grant_writer", END)

outreach_graph = builder.compile()