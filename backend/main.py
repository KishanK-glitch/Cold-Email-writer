import os
import uuid
import hashlib
import traceback
from dotenv import load_dotenv

# Load .env first so that API keys are available when modules are imported
load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import JobRequest, JobResponse, StatusResponse
from backend.graph import outreach_graph

app = FastAPI(title="Autonomous Cold Outreach System – MIP-003", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store  {job_id: {"status": str, "email": str|None, "output_hash": str|None}}
JOBS_DB: dict = {}


# ─── Helpers ────────────────────────────────────────────────────────────────

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _run_graph(job_id: str, url: str, user_offering: str) -> None:
    """Background task: invoke the LangChain graph and persist the result."""
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
        result = outreach_graph.invoke(initial_state)

        if result.get("error"):
            JOBS_DB[job_id]["status"] = "failed"
            JOBS_DB[job_id]["email_output"] = result["error"]
            return

        email_text: str = result.get("email") or ""
        JOBS_DB[job_id]["status"] = "completed"
        JOBS_DB[job_id]["email_output"] = email_text
        JOBS_DB[job_id]["output_hash"] = _sha256(email_text)

    except Exception:
        traceback.print_exc()
        JOBS_DB[job_id]["status"] = "failed"
        JOBS_DB[job_id]["email_output"] = "Internal error during graph execution."


# ─── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Autonomous Cold Outreach System (MIP-003) is running."}


@app.post("/start_job", response_model=JobResponse)
async def start_job(request: JobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    # Deterministic hash of the raw input payload
    raw_input = f"{request.input_data.url}::{request.input_data.user_offering}"
    input_hash = _sha256(raw_input)

    # Persist initial state
    JOBS_DB[job_id] = {"status": "pending", "email_output": None, "output_hash": None}

    # Fire-and-forget graph execution
    background_tasks.add_task(
        _run_graph,
        job_id,
        request.input_data.url,
        request.input_data.user_offering,
    )

    return JobResponse(
        job_id=job_id,
        identifier_from_purchaser=request.identifier_from_purchaser,
        input_hash=input_hash,
    )


@app.get("/status", response_model=StatusResponse)
async def get_status(job_id: str):
    job = JOBS_DB.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return StatusResponse(
        status=job["status"],
        email_output=job.get("email_output"),
        output_hash=job.get("output_hash"),
    )
