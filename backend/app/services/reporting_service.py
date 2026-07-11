from datetime import date
from typing import Any

from sqlmodel import Session

from app.core.config import settings
from app.models import Report
from app.services.finance_service import get_financial_summary
from app.services.program_service import get_program_status, list_programs
from app.services.volunteer_service import list_opportunities, list_volunteers
from app.tools.report_generators import export_excel, export_pdf, export_word


def build_program_dashboard(session: Session, organization_id: int) -> list[dict[str, Any]]:
    programs = list_programs(session, organization_id)
    return [get_program_status(session, p.id) for p in programs]


def build_volunteer_summary(session: Session, organization_id: int | None = None) -> dict[str, Any]:
    volunteers = list_volunteers(session)
    opportunities = list_opportunities(session, organization_id=organization_id)
    return {
        "total_volunteers": len(volunteers),
        "active_volunteers": len([v for v in volunteers if v.status == "active"]),
        "total_opportunities": len(opportunities),
        "open_opportunities": len([o for o in opportunities if o.status == "open"]),
    }


def generate_report(
    session: Session,
    organization_id: int,
    report_type: str,
    period: str | None,
    output_format: str = "pdf",
) -> Report:
    """Generate a report combining program, volunteer, and financial data."""
    period = period or date.today().strftime("%Y-%m")
    data: dict[str, Any] = {
        "organization_id": organization_id,
        "report_type": report_type,
        "period": period,
        "generated_at": date.today().isoformat(),
        "programs": build_program_dashboard(session, organization_id),
        "volunteers": build_volunteer_summary(session, organization_id),
        "finance": get_financial_summary(session, organization_id),
    }

    file_path = None
    if output_format in ("pdf", "word", "excel"):
        safe_period = period.replace(" ", "_").replace("/", "-")
        base_name = f"{report_type}_{safe_period}"
        if output_format == "pdf":
            file_path = export_pdf(data, base_name, settings.arabic_font_path)
        elif output_format == "word":
            file_path = export_word(data, base_name)
        elif output_format == "excel":
            file_path = export_excel(data, base_name)

    report = Report(
        organization_id=organization_id,
        report_type=report_type,
        period=period,
        data=data,
        file_path=file_path,
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return report
