from datetime import date
from typing import Any

from sqlmodel import Session, select

from app.models import Activity, KPI, Program


def create_program(session: Session, data: dict[str, Any]) -> Program:
    program = Program(**data)
    session.add(program)
    session.commit()
    session.refresh(program)
    return program


def list_programs(session: Session, organization_id: int | None = None) -> list[Program]:
    stmt = select(Program)
    if organization_id is not None:
        stmt = stmt.where(Program.organization_id == organization_id)
    return list(session.exec(stmt).all())


def get_program(session: Session, program_id: int) -> Program | None:
    return session.get(Program, program_id)


def update_program(session: Session, program_id: int, data: dict[str, Any]) -> Program | None:
    program = session.get(Program, program_id)
    if not program:
        return None
    for key, value in data.items():
        if hasattr(program, key):
            setattr(program, key, value)
    session.add(program)
    session.commit()
    session.refresh(program)
    return program


def add_activity(session: Session, program_id: int, data: dict[str, Any]) -> Activity:
    activity = Activity(program_id=program_id, **data)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def list_activities(session: Session, program_id: int | None = None) -> list[Activity]:
    stmt = select(Activity)
    if program_id is not None:
        stmt = stmt.where(Activity.program_id == program_id)
    return list(session.exec(stmt).all())


def add_kpi(session: Session, program_id: int, data: dict[str, Any]) -> KPI:
    kpi = KPI(program_id=program_id, **data)
    session.add(kpi)
    session.commit()
    session.refresh(kpi)
    return kpi


def list_kpis(session: Session, program_id: int | None = None) -> list[KPI]:
    stmt = select(KPI)
    if program_id is not None:
        stmt = stmt.where(KPI.program_id == program_id)
    return list(session.exec(stmt).all())


def update_kpi(session: Session, kpi_id: int, actual_value: float) -> KPI | None:
    kpi = session.get(KPI, kpi_id)
    if not kpi:
        return None
    kpi.actual_value = actual_value
    session.add(kpi)
    session.commit()
    session.refresh(kpi)
    return kpi


def update_activity(session: Session, activity_id: int, data: dict[str, Any]) -> Activity | None:
    activity = session.get(Activity, activity_id)
    if not activity:
        return None
    for key, value in data.items():
        if hasattr(activity, key):
            setattr(activity, key, value)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def get_program_status(session: Session, program_id: int) -> dict[str, Any]:
    program = session.get(Program, program_id)
    if not program:
        return {"error": "Program not found"}

    activities = list_activities(session, program_id)
    kpis = list_kpis(session, program_id)

    total_activities = len(activities)
    completed_activities = sum(1 for a in activities if a.status == "completed")
    activity_progress = (completed_activities / total_activities * 100) if total_activities else 0.0

    kpi_progress = 0.0
    if kpis:
        kpi_progress = sum(
            (k.actual_value or 0) / k.target_value * 100 for k in kpis if k.target_value
        ) / len(kpis)

    overall = (activity_progress + kpi_progress) / 2 if kpis else activity_progress

    if overall >= 90:
        computed_status = "منجز"
    elif overall >= 50:
        computed_status = "نشط"
    elif any(a.status == "blocked" for a in activities):
        computed_status = "متعطل"
    elif date.today() > (program.end_date or date.max) and overall < 100:
        computed_status = "متأخر"
    else:
        status_map = {
            "planned": "مخطط",
            "active": "نشط",
            "completed": "منجز",
            "delayed": "متأخر",
            "blocked": "متعطل",
        }
        computed_status = status_map.get(program.status, program.status)

    return {
        "program_id": program.id,
        "name": program.name,
        "status": computed_status,
        "activity_progress": round(activity_progress, 2),
        "kpi_progress": round(kpi_progress, 2),
        "overall_progress": round(overall, 2),
        "activities": total_activities,
        "completed_activities": completed_activities,
        "kpis": len(kpis),
    }
