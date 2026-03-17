from fastapi import FastAPI, HTTPException
from backend.models import OutreachRequest, OutreachResponse
from backend.graph import outreach_graph

app = FastAPI(title="Autonomous Cold Outreach System", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Autonomous Cold Outreach System is running. Use /generate_email to start workflows."}

@app.post("/generate_email", response_model=OutreachResponse)
async def generate_email(request: OutreachRequest):
    initial_state = {
        "url": request.url,
        "user_offering": request.user_offering,
        "scraped_content": "",
        "company_dna": None,
        "hook": None,
        "email": None,
        "error": None
    }
    
    try:
        # Run graph
        result = outreach_graph.invoke(initial_state)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
            
        company_dna_dict = None
        if result.get("company_dna"):
            company_dna_dict = result["company_dna"].model_dump()
            
        return dict(
            email=result.get("email"),
            company_dna=company_dna_dict,
            hook=result.get("hook")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
