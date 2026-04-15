from masumi.hitl import request_input
from backend.graph import outreach_graph

async def process_job(identifier_from_purchaser: str, input_data: dict) -> str:
    url = input_data.get("url", "")
    current_offering = input_data.get("user_offering", "")
    
    # The HITL Iteration Loop
    while True:
        # 1. Execute the LangGraph workflow
        final_state = outreach_graph.invoke({
            "url": url, 
            "user_offering": current_offering
        })
        
        # Catch any scraping or API errors immediately
        if final_state.get("error"):
            return f"Agent Execution Failed: {final_state.get('error')}"
            
        draft = final_state.get("email", "Error: No draft generated.")
        
        # 2. The HITL Checkpoint: Pause execution and push to the UI
        human_review = await request_input(
            {
                "input_data": [
                    {
                        "id": "approve",
                        "type": "boolean",
                        "name": "Approve Email Draft?",
                        "data": {"description": f"Generated Draft:\n\n{draft}"}
                    },
                    {
                        "id": "feedback",
                        "type": "string",
                        "name": "Rewrite Feedback",
                        "data": {"description": "If rejecting, tell the AI exactly what to change."}
                    }
                ]
            },
            message="Please review the drafted email. Approve to finalize, or provide feedback for a rewrite."
        )
        
        # 3. Process the human's decision
        is_approved = human_review.get("approve", False)
        feedback = human_review.get("feedback", "")
        
        if is_approved:
            # Human signed off. Return the final string to settle the smart contract.
            return draft
            
        if not is_approved and not feedback:
            # Human rejected it but didn't say why. Kill the job.
            return "Job cancelled by user: Draft rejected with no rewrite feedback."
            
        # 4. Human rejected it WITH feedback. Append it to the prompt and loop again.
        current_offering = f"{current_offering}\n\n[USER FEEDBACK FOR NEXT DRAFT: {feedback}]"