from datetime import date, timedelta

from sqlmodel import select

from app.database import SessionLocal
from app.models import (
    Activity,
    Budget,
    KPI,
    Organization,
    Program,
    Transaction,
    Volunteer,
    VolunteerEnrollment,
    VolunteerHour,
    VolunteerOpportunity,
)
from app.services.reporting_service import generate_report


def seed_data() -> None:
    with SessionLocal() as session:
        # Seed organization once
        existing = session.exec(
            select(Organization).where(Organization.name == "جمعية الأمل الخيرية")
        ).first()
        if existing:
            return

        org = Organization(
            name="جمعية الأمل الخيرية",
            ncnp_license="NCNP-123456",
            contact_email="info@al-amal.org",
            contact_phone="+966501234567",
        )
        session.add(org)
        session.commit()
        session.refresh(org)

        # Program
        program = Program(
            organization_id=org.id,
            name="برنامج التعليم المجتمعي",
            description="دعم الطلاب المحتاجين بالقرى والهجر",
            goals="تحسين مستوى التحصيل الدراسي لـ 500 طالب",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            status="active",
        )
        session.add(program)
        session.commit()
        session.refresh(program)

        # Activities
        activities = [
            Activity(program_id=program.id, name="توزيع حقائب مدرسية", planned_date=date.today() - timedelta(days=15), status="completed"),
            Activity(program_id=program.id, name="إقامة دورات تقوية", planned_date=date.today(), status="in_progress"),
            Activity(program_id=program.id, name="تكريم الطلاب المتفوقين", planned_date=date.today() + timedelta(days=30), status="planned"),
        ]
        session.add_all(activities)

        # KPIs
        kpis = [
            KPI(program_id=program.id, name="عدد الطلاب المستفيدين", target_value=500, actual_value=320, unit="طالب"),
            KPI(program_id=program.id, name="نسبة التحسن في التحصيل", target_value=20, actual_value=15, unit="%"),
        ]
        session.add_all(kpis)

        # Volunteers
        volunteer1 = Volunteer(name="محمد العلي", email="mohammed@example.com", phone="0501111111", national_id="1234567890", skills=["تدريس", "تنظيم"])
        volunteer2 = Volunteer(name="فاطمة الزهراء", email="fatima@example.com", phone="0502222222", national_id="0987654321", skills=["تدريس", "إعلام"])
        session.add_all([volunteer1, volunteer2])
        session.commit()
        session.refresh(volunteer1)
        session.refresh(volunteer2)

        # Opportunity
        opportunity = VolunteerOpportunity(
            organization_id=org.id,
            program_id=program.id,
            name="معلم متطوع",
            description="تدريس الطلاب في المواد الأساسية",
            required_skills=["تدريس"],
            location="الرياض",
            opportunity_date=date.today(),
            status="open",
        )
        session.add(opportunity)
        session.commit()
        session.refresh(opportunity)

        # Enrollment
        enrollment = VolunteerEnrollment(volunteer_id=volunteer1.id, opportunity_id=opportunity.id, status="completed", hours=12)
        session.add(enrollment)

        # Hours
        session.add_all(
            [
                VolunteerHour(volunteer_id=volunteer1.id, opportunity_id=opportunity.id, hours_date=date.today() - timedelta(days=10), hours=6, description="تدريس رياضيات"),
                VolunteerHour(volunteer_id=volunteer1.id, opportunity_id=opportunity.id, hours_date=date.today() - timedelta(days=5), hours=6, description="تدريس علوم"),
            ]
        )

        # Budget
        budget = Budget(organization_id=org.id, name="موازنة البرامج 2026", fiscal_year="2026", total=100000.0)
        session.add(budget)
        session.commit()
        session.refresh(budget)

        # Transactions
        transactions = [
            Transaction(organization_id=org.id, budget_id=budget.id, type="income", source="donation", amount=50000.0, transaction_date=date.today() - timedelta(days=20), description="تبرع كريم من أحد المؤسسات", donor_name="شركة الأمل"),
            Transaction(organization_id=org.id, budget_id=budget.id, type="expense", source="operational", amount=15000.0, transaction_date=date.today() - timedelta(days=10), description="شراء حقائب مدرسية وقرطاسية"),
            Transaction(organization_id=org.id, budget_id=budget.id, type="expense", source="operational", amount=5000.0, transaction_date=date.today() - timedelta(days=5), description="مصاريف نقل للدورات"),
        ]
        session.add_all(transactions)

        session.commit()

        # Generate a sample report
        try:
            generate_report(session, org.id, "monthly", date.today().strftime("%Y-%m"), output_format="pdf")
        except Exception:
            pass


if __name__ == "__main__":
    seed_data()
