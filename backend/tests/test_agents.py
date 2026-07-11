from datetime import date

from app.agents.governance_agent import governance_agent
from app.agents.program_agent import program_agent
from app.agents.reporting_agent import reporting_agent
from app.agents.volunteer_agent import volunteer_agent


def test_program_agent_create(db_session):
    result = program_agent.run_direct(
        db_session,
        {"action": "create", "data": {"name": "برنامج اختبار", "organization_id": 1, "status": "active"}},
    )
    assert result["agent"] == "program"
    assert result["action"] == "create"
    assert result["program"]["name"] == "برنامج اختبار"


def test_program_agent_status(db_session):
    result = program_agent.run_direct(db_session, {"action": "list"})
    assert result["agent"] == "program"
    assert "programs" in result


def test_volunteer_agent_create(db_session):
    result = volunteer_agent.run_direct(
        db_session,
        {"action": "create", "data": {"name": "أحمد", "email": "ahmed@example.com", "skills": ["تدريس"]}},
    )
    assert result["agent"] == "volunteer"
    assert result["action"] == "create"
    assert result["volunteer"]["name"] == "أحمد"


def test_volunteer_agent_match(db_session):
    result = volunteer_agent.run_direct(db_session, {"action": "match", "opportunity_id": 1})
    assert result["agent"] == "volunteer"
    assert "matches" in result


def test_governance_agent_financial_summary(db_session):
    result = governance_agent.run_direct(db_session, {"action": "financial_summary", "organization_id": 1})
    assert result["agent"] == "governance"
    assert result["action"] == "financial_summary"
    assert "summary" in result


def test_governance_agent_compliance(db_session):
    result = governance_agent.run_direct(db_session, {"action": "check_compliance", "organization_id": 1})
    assert result["agent"] == "governance"
    assert result["action"] == "check_compliance"
    assert "checks" in result


def test_reporting_agent_dashboard(db_session):
    result = reporting_agent.run_direct(db_session, {"action": "dashboard", "organization_id": 1})
    assert result["agent"] == "reporting"
    assert "programs" in result
    assert "volunteers" in result
    assert "finance" in result


def test_reporting_agent_generate_pdf(db_session, tmp_path):
    result = reporting_agent.run_direct(
        db_session,
        {"action": "generate", "organization_id": 1, "report_type": "monthly", "period": "2026-01", "format": "pdf"},
    )
    assert result["agent"] == "reporting"
    assert result["action"] == "generate"
    assert result["file_path"]
    assert result["file_path"].endswith(".pdf")
