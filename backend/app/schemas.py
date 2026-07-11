from datetime import date
from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    user_id: str | None = None


class AgentRunRequest(BaseModel):
    agent: str
    payload: dict[str, Any] | None = None


class ReportRequest(BaseModel):
    report_type: str
    period: str | None = None
    organization_id: int | None = None
    format: str = "pdf"  # pdf, word, excel


class ProgramCreate(BaseModel):
    organization_id: int
    name: str
    description: str | None = None
    goals: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = "planned"


class VolunteerCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    national_id: str | None = None
    date_of_birth: date | None = None
    skills: list[str] | None = None


class TransactionCreate(BaseModel):
    organization_id: int
    budget_id: int | None = None
    type: str
    source: str | None = None
    amount: float
    transaction_date: date
    description: str | None = None
    donor_name: str | None = None
    donor_email: str | None = None


class OpportunityCreate(BaseModel):
    organization_id: int
    program_id: int | None = None
    name: str
    description: str | None = None
    required_skills: list[str] | None = None
    location: str | None = None
    opportunity_date: date | None = None


class BudgetCreate(BaseModel):
    organization_id: int
    name: str
    fiscal_year: str
    total: float


class ComplianceResponse(BaseModel):
    status: str
    details: str
    source_url: str | None = None


class ReportResponse(BaseModel):
    report_type: str
    period: str | None = None
    file_path: str | None = None
    download_url: str | None = None
    message: str
