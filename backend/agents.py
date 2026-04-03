import traceback
from backend.graph import outreach_graph

async def process_job(identifier_from_purchaser: str, input_data: dict):
    # Extract inputs matching the schema we will define in main.py
    url = input_data.get("url")
    user_offering = input_data.get("user_offering")
    
    initial_state = {
        "url": url,
        "user_offering": user_offering,
        "scraped_content": "",
        "company_dna": None,
        "hook": None,
        "email": None,
        "error": None,
    }
    
    try:
        # Run your existing LangGraph setup
        result = outreach_graph.invoke(initial_state)

        if result.get("error"):
            return f"Execution Failed: {result['error']}"

        # Return the generated email text
        return result.get("email") or "Task completed, but no email generated."

    except Exception as e:
        traceback.print_exc()
        return f"Internal error during graph execution: {str(e)}"