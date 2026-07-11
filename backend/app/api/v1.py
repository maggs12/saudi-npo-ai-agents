from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.agents.governance_agent import governance_agent
from app.agents.orchestrator import get_orchestrator
from app.agents.program_agent import program_agent
from app.agents.reporting_agent import reporting_agent
from app.agents.volunteer_agent import volunteer_agent
from app.dependencies import api_key_header
from app.database import create_db_and_tables, get_session
from app.schemas import (
    AgentRunRequest,
    BudgetCreate,
    ChatRequest,
    OpportunityCreate,
    ProgramCreate,
    ReportRequest,
    TransactionCreate,
    VolunteerCreate,
)
from app.services import finance_service, program_service, regulation_service, reporting_service, volunteer_service

router = APIRouter(prefix="/api/v1", dependencies=[Depends(api_key_header)])


@router.post("/chat")
def chat(request: ChatRequest, session: Session = Depends(get_session)) -> dict[str, Any]:
    orchestrator = get_orchestrator(session)
    return orchestrator.invoke(request.message, thread_id=request.thread_id, user_id=request.user_id)


@router.post("/agents/{agent_name}/run")
def run_agent(
    agent_name: str,
    request: AgentRunRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    agents = {
        "program": program_agent,
        "volunteer": volunteer_agent,
        "governance": governance_agent,
        "reporting": reporting_agent,
    }
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agents[agent_name]
    payload = request.payload or {}
    return agent.run_direct(session, payload)


# Programs
@router.get("/programs")
def list_programs(organization_id: int | None = None, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    programs = program_service.list_programs(session, organization_id)
    return [p.model_dump() for p in programs]


@router.post("/programs")
def create_program(request: ProgramCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    program = program_service.create_program(session, request.model_dump())
    return program.model_dump()


@router.get("/programs/{program_id}/status")
def get_program_status(program_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    status = program_service.get_program_status(session, program_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status


@router.post("/programs/{program_id}/activities")
def add_activity(program_id: int, data: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any]:
    activity = program_service.add_activity(session, program_id, data)
    return activity.model_dump()


@router.post("/programs/{program_id}/kpis")
def add_kpi(program_id: int, data: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any]:
    kpi = program_service.add_kpi(session, program_id, data)
    return kpi.model_dump()


# Volunteers
@router.get("/volunteers")
def list_volunteers(status: str | None = None, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    volunteers = volunteer_service.list_volunteers(session, status)
    return [v.model_dump() for v in volunteers]


@router.post("/volunteers")
def create_volunteer(request: VolunteerCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    volunteer = volunteer_service.create_volunteer(session, request.model_dump())
    return volunteer.model_dump()


@router.get("/volunteers/{volunteer_id}")
def get_volunteer(volunteer_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    volunteer = volunteer_service.get_volunteer(session, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return volunteer.model_dump()


@router.get("/volunteers/{volunteer_id}/hours")
def get_volunteer_hours(volunteer_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    return {"volunteer_id": volunteer_id, "total_hours": volunteer_service.get_total_hours(session, volunteer_id)}


@router.post("/volunteers/{volunteer_id}/hours")
def log_volunteer_hours(volunteer_id: int, data: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any]:
    data["volunteer_id"] = volunteer_id
    record = volunteer_service.log_hours(session, data)
    return record.model_dump()


@router.get("/opportunities")
def list_opportunities(organization_id: int | None = None, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    opportunities = volunteer_service.list_opportunities(session, organization_id=organization_id)
    return [o.model_dump() for o in opportunities]


@router.post("/opportunities")
def create_opportunity(request: OpportunityCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    opportunity = volunteer_service.create_opportunity(session, request.model_dump())
    return opportunity.model_dump()


@router.post("/opportunities/{opportunity_id}/match")
def match_opportunity(opportunity_id: int, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return volunteer_service.match_volunteers(session, opportunity_id)


@router.post("/enrollments")
def register_volunteer(data: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any]:
    enrollment = volunteer_service.register_volunteer(
        session, data["volunteer_id"], data["opportunity_id"]
    )
    return enrollment.model_dump()


@router.post("/certificates")
def issue_certificate(data: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any] | None:
    cert = volunteer_service.issue_certificate(
        session, data["volunteer_id"], data.get("opportunity_id")
    )
    if not cert:
        raise HTTPException(status_code=400, detail="Could not issue certificate")
    return cert


# Finance
@router.get("/budgets")
def list_budgets(organization_id: int | None = None, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    budgets = finance_service.list_budgets(session, organization_id)
    return [b.model_dump() for b in budgets]


@router.post("/budgets")
def create_budget(request: BudgetCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    budget = finance_service.create_budget(session, request.model_dump())
    return budget.model_dump()


@router.get("/budgets/{budget_id}/status")
def get_budget_status(budget_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    status = finance_service.get_budget_status(session, budget_id)
    if not status:
        raise HTTPException(status_code=404, detail="Budget not found")
    return status


@router.get("/transactions")
def list_transactions(organization_id: int | None = None, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    transactions = finance_service.list_transactions(session, organization_id)
    return [t.model_dump() for t in transactions]


@router.post("/transactions")
def create_transaction(request: TransactionCreate, session: Session = Depends(get_session)) -> dict[str, Any]:
    transaction = finance_service.record_transaction(session, request.model_dump())
    return transaction.model_dump()


@router.get("/finance/summary")
def get_financial_summary(organization_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    return finance_service.get_financial_summary(session, organization_id)


@router.post("/compliance/check")
def check_compliance(organization_id: int, session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    checks = finance_service.check_compliance(session, organization_id)
    return [c.model_dump() for c in checks]


# Regulations
@router.post("/regulations/search")
def search_regulations(query: dict[str, Any], session: Session = Depends(get_session)) -> dict[str, Any]:
    q = query.get("query", "")
    local = regulation_service.search_regulations_with_fallback(session, q, top_k=3)
    web = regulation_service.web_search(q, max_results=3)
    return {"query": q, "local_results": local, "web_results": web}


# Reports
@router.post("/reports")
def generate_report(request: ReportRequest, session: Session = Depends(get_session)) -> dict[str, Any]:
    report = reporting_service.generate_report(
        session,
        organization_id=request.organization_id or 1,
        report_type=request.report_type,
        period=request.period,
        output_format=request.format,
    )
    return {
        "report": report.model_dump(),
        "file_path": report.file_path,
        "download_url": f"/api/v1/reports/{report.id}/download",
    }


@router.get("/reports/{report_id}")
def get_report(report_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    from sqlmodel import select
    from app.models import Report

    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()


@router.get("/reports/{report_id}/download")
def download_report(report_id: int, session: Session = Depends(get_session)):
    from fastapi.responses import FileResponse
    from sqlmodel import select
    from app.models import Report

    report = session.get(Report, report_id)
    if not report or not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(report.file_path, filename=report.file_path.split("/")[-1])


# Dashboard
@router.get("/dashboard")
def dashboard(organization_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    return {
        "programs": reporting_service.build_program_dashboard(session, organization_id),
        "volunteers": reporting_service.build_volunteer_summary(session, organization_id),
        "finance": finance_service.get_financial_summary(session, organization_id),
    }


# Seed trigger
@router.post("/seed")
def seed_database() -> dict[str, str]:
    create_db_and_tables()
    from app.seed import seed_data

    seed_data()
    return {"status": "seeded"}
