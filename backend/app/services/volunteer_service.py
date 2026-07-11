from datetime import date
from typing import Any

from sqlmodel import Session, select

from app.models import (
    Skill,
    Volunteer,
    VolunteerEnrollment,
    VolunteerHour,
    VolunteerOpportunity,
    VolunteerSkill,
)


def create_volunteer(session: Session, data: dict[str, Any]) -> Volunteer:
    skills = data.pop("skills", None) or []
    volunteer = Volunteer(**data)
    volunteer.skills = skills
    session.add(volunteer)
    session.commit()
    session.refresh(volunteer)

    for skill_name in skills:
        skill = session.exec(select(Skill).where(Skill.name == skill_name)).first()
        if not skill:
            skill = Skill(name=skill_name)
            session.add(skill)
            session.commit()
            session.refresh(skill)
        session.add(VolunteerSkill(volunteer_id=volunteer.id, skill_id=skill.id))
    session.commit()
    session.refresh(volunteer)
    return volunteer


def list_volunteers(session: Session, status: str | None = None) -> list[Volunteer]:
    stmt = select(Volunteer)
    if status:
        stmt = stmt.where(Volunteer.status == status)
    return list(session.exec(stmt).all())


def get_volunteer(session: Session, volunteer_id: int) -> Volunteer | None:
    return session.get(Volunteer, volunteer_id)


def create_opportunity(session: Session, data: dict[str, Any]) -> VolunteerOpportunity:
    opportunity = VolunteerOpportunity(**data)
    session.add(opportunity)
    session.commit()
    session.refresh(opportunity)
    return opportunity


def list_opportunities(
    session: Session, organization_id: int | None = None, status: str | None = None
) -> list[VolunteerOpportunity]:
    stmt = select(VolunteerOpportunity)
    if organization_id is not None:
        stmt = stmt.where(VolunteerOpportunity.organization_id == organization_id)
    if status:
        stmt = stmt.where(VolunteerOpportunity.status == status)
    return list(session.exec(stmt).all())


def match_volunteers(session: Session, opportunity_id: int) -> list[dict[str, Any]]:
    opportunity = session.get(VolunteerOpportunity, opportunity_id)
    if not opportunity:
        return []

    required = set(opportunity.required_skills or [])
    volunteers = list_volunteers(session)
    results = []
    for volunteer in volunteers:
        volunteer_skills = set(volunteer.skills or [])
        matched = required & volunteer_skills if required else True
        if matched:
            results.append(
                {
                    "volunteer_id": volunteer.id,
                    "name": volunteer.name,
                    "skills": volunteer.skills,
                    "matched_skills": list(required & volunteer_skills) if required else [],
                }
            )
    return results


def register_volunteer(session: Session, volunteer_id: int, opportunity_id: int) -> VolunteerEnrollment:
    enrollment = VolunteerEnrollment(
        volunteer_id=volunteer_id,
        opportunity_id=opportunity_id,
        status="registered",
    )
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment


def log_hours(session: Session, data: dict[str, Any]) -> VolunteerHour:
    record = VolunteerHour(**data)
    session.add(record)
    session.commit()
    session.refresh(record)

    # Update enrollment hours if it exists
    stmt = select(VolunteerEnrollment).where(
        VolunteerEnrollment.volunteer_id == record.volunteer_id,
        VolunteerEnrollment.opportunity_id == record.opportunity_id,
    )
    enrollment = session.exec(stmt).first()
    if enrollment:
        enrollment.hours = (enrollment.hours or 0) + record.hours
        session.add(enrollment)
        session.commit()
        session.refresh(record)

    return record


def get_total_hours(session: Session, volunteer_id: int) -> float:
    from sqlalchemy import func

    result = session.exec(
        select(func.sum(VolunteerHour.hours)).where(VolunteerHour.volunteer_id == volunteer_id)
    ).first()
    return result or 0.0


def issue_certificate(session: Session, volunteer_id: int, opportunity_id: int) -> dict[str, Any] | None:
    from sqlalchemy import func

    stmt = select(func.sum(VolunteerHour.hours)).where(
        VolunteerHour.volunteer_id == volunteer_id,
        VolunteerHour.opportunity_id == opportunity_id,
    )
    total = session.exec(stmt).first() or 0.0

    enrollment = session.exec(
        select(VolunteerEnrollment).where(
            VolunteerEnrollment.volunteer_id == volunteer_id,
            VolunteerEnrollment.opportunity_id == opportunity_id,
        )
    ).first()
    if not enrollment:
        return None

    enrollment.certificate_issued = True
    enrollment.status = "completed"
    session.add(enrollment)
    session.commit()

    opportunity = session.get(VolunteerOpportunity, opportunity_id)
    volunteer = session.get(Volunteer, volunteer_id)

    return {
        "certificate_id": f"CERT-{volunteer_id}-{opportunity_id}",
        "volunteer_name": volunteer.name if volunteer else None,
        "opportunity_name": opportunity.name if opportunity else None,
        "hours": total,
        "issued_at": date.today().isoformat(),
    }
