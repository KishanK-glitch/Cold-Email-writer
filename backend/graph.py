from langgraph.graph import StateGraph, END
from backend.models import AgentState
from backend.utils import scrape_url
from backend.agent import researcher_node, strategist_node, copywriter_node

def scrape_node(state: AgentState):
    url = state.get("url")
    try:
        content = scrape_url(url)
        return {"scraped_content": content}
    except Exception as e:
        return {"error": str(e)}

def route_after_scrape(state: AgentState):
    if state.get("error"):
        return END
    return "researcher"

def route_after_researcher(state: AgentState):
    if state.get("error"):
        return END
    return "strategist"

def route_after_strategist(state: AgentState):
    if state.get("error"):
        return END
    return "copywriter"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("scrape", scrape_node)
builder.add_node("researcher", researcher_node)
builder.add_node("strategist", strategist_node)
builder.add_node("copywriter", copywriter_node)

builder.set_entry_point("scrape")
builder.add_conditional_edges("scrape", route_after_scrape)
builder.add_conditional_edges("researcher", route_after_researcher)
builder.add_conditional_edges("strategist", route_after_strategist)
builder.add_edge("copywriter", END)

outreach_graph = builder.compile()
