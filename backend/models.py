from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Dict, Any

# ─── LangChain / Graph internals ────────────────────────────────

class CompanyDNA(BaseModel):
    value_proposition: str = Field(description="The core value proposition of the company")
    target_audience: str = Field(description="The primary target audience or ideal customer profile")
    recent_news: str = Field(description="Recent news, updates, or key features mentioned")

class AgentState(TypedDict):
    url: str
    user_offering: str
    scraped_content: str
    company_dna: Optional[CompanyDNA]
    user_intent: Optional[str]  # NEW: 'sales', 'partnership', or 'grant'
    email: Optional[str]
    error: Optional[str]

# ─── MIP-003 API contracts (unchanged) ───────────────────────────────────────

class InputData(BaseModel):
    url: str
    user_offering: str

class JobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: InputData

class JobResponse(BaseModel):
    job_id: str
    agent_id: str = "cold-email-agent"
    sellerVKey: str = "placeholder"
    identifier_from_purchaser: str
    input_hash: str

class StatusResponse(BaseModel):
    status: str                        # "pending" | "completed" | "failed"
    email_output: Optional[str] = None
    output_hash: Optional[str] = None