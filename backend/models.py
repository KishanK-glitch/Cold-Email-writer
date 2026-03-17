from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Dict, Any

class CompanyDNA(BaseModel):
    value_proposition: str = Field(description="The core value proposition of the company")
    target_audience: str = Field(description="The primary target audience or ideal customer profile")
    recent_news: str = Field(description="Recent news, updates, or key features mentioned")

class AgentState(TypedDict):
    url: str
    user_offering: str
    scraped_content: str
    company_dna: Optional[CompanyDNA]
    hook: Optional[str]
    email: Optional[str]
    error: Optional[str]

class OutreachRequest(BaseModel):
    url: str
    user_offering: str

class OutreachResponse(BaseModel):
    email: Optional[str] = None
    company_dna: Optional[Dict[str, Any]] = None
    hook: Optional[str] = None
    error: Optional[str] = None
