from datetime import date, datetime
from typing import Any, Literal

from pgvector.sqlalchemy import VECTOR
from sqlmodel import Field, SQLModel

from app.database import EncryptedString, JSONDict


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Organization(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    logo_url: str | None = Field(default=None)
    ncnp_license: str | None = Field(default=None)
    contact_email: str | None = Field(default=None)
    contact_phone: str | None = Field(default=None)


class Program(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    name: str
    description: str | None = Field(default=None)
    goals: str | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    status: str = Field(default="planned")  # planned, active, completed, delayed, blocked


class Activity(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="program.id")
    name: str
    description: str | None = Field(default=None)
    planned_date: date | None = Field(default=None)
    actual_date: date | None = Field(default=None)
    status: str = Field(default="planned")  # planned, in_progress, completed, cancelled


class KPI(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="program.id")
    name: str
    target_value: float | None = Field(default=None)
    actual_value: float | None = Field(default=None)
    unit: str | None = Field(default=None)


class Skill(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class Volunteer(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None = Field(default=None)
    phone: str | None = Field(default=None, sa_type=EncryptedString())
    national_id: str | None = Field(default=None, sa_type=EncryptedString())
    date_of_birth: date | None = Field(default=None)
    status: str = Field(default="active")  # active, inactive
    skills: list[str] | None = Field(default=None, sa_type=JSONDict())


class VolunteerSkill(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    volunteer_id: int = Field(foreign_key="volunteer.id")
    skill_id: int = Field(foreign_key="skill.id")


class VolunteerOpportunity(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    program_id: int | None = Field(default=None, foreign_key="program.id")
    name: str
    description: str | None = Field(default=None)
    required_skills: list[str] | None = Field(default=None, sa_type=JSONDict())
    location: str | None = Field(default=None)
    opportunity_date: date | None = Field(default=None)
    status: str = Field(default="open")  # open, closed, completed


class VolunteerEnrollment(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    volunteer_id: int = Field(foreign_key="volunteer.id")
    opportunity_id: int = Field(foreign_key="volunteeropportunity.id")
    status: str = Field(default="registered")  # registered, attended, completed, cancelled
    hours: float | None = Field(default=None)
    certificate_issued: bool = Field(default=False)


class VolunteerHour(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    volunteer_id: int = Field(foreign_key="volunteer.id")
    opportunity_id: int | None = Field(default=None, foreign_key="volunteeropportunity.id")
    hours_date: date
    hours: float
    description: str | None = Field(default=None)


class Budget(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    name: str
    fiscal_year: str
    total: float


class Transaction(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    budget_id: int | None = Field(default=None, foreign_key="budget.id")
    type: str = Field(default="expense")  # income, expense
    source: str | None = Field(default=None)  # donation, sponsorship, grant, operational, other
    amount: float
    transaction_date: date
    description: str | None = Field(default=None)
    donor_name: str | None = Field(default=None)
    donor_email: str | None = Field(default=None, sa_type=EncryptedString())


class ComplianceCheck(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    rule: str
    status: str = Field(default="pass")  # pass, fail, warning
    details: str | None = Field(default=None)
    source_url: str | None = Field(default=None)


class Regulation(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_url: str
    title: str
    content: str | None = Field(default=None)
    embedding: list[float] | None = Field(default=None, sa_type=VECTOR(384))


class Report(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    report_type: str
    period: str | None = Field(default=None)
    data: dict[str, Any] | None = Field(default=None, sa_type=JSONDict())
    file_path: str | None = Field(default=None)


class AuditLog(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    organization_id: int | None = Field(default=None)
    table_name: str
    record_id: int | None = Field(default=None)
    action: str
    user_id: str | None = Field(default=None)
    changes: dict[str, Any] | None = Field(default=None, sa_type=JSONDict())


class Conversation(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    thread_id: str
    role: str  # human, ai, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
