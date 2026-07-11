from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Budget, ComplianceCheck, Transaction


def create_budget(session: Session, data: dict[str, Any]) -> Budget:
    budget = Budget(**data)
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


def list_budgets(session: Session, organization_id: int | None = None) -> list[Budget]:
    stmt = select(Budget)
    if organization_id is not None:
        stmt = stmt.where(Budget.organization_id == organization_id)
    return list(session.exec(stmt).all())


def get_budget_status(session: Session, budget_id: int) -> dict[str, Any] | None:
    budget = session.get(Budget, budget_id)
    if not budget:
        return None

    spent = session.exec(
        select(func.sum(Transaction.amount)).where(
            Transaction.budget_id == budget_id,
            Transaction.type == "expense",
        )
    ).first() or 0.0

    income = session.exec(
        select(func.sum(Transaction.amount)).where(
            Transaction.budget_id == budget_id,
            Transaction.type == "income",
        )
    ).first() or 0.0

    return {
        "budget_id": budget.id,
        "name": budget.name,
        "fiscal_year": budget.fiscal_year,
        "total": budget.total,
        "spent": spent,
        "income": income,
        "remaining": budget.total - spent,
    }


def record_transaction(session: Session, data: dict[str, Any]) -> Transaction:
    transaction = Transaction(**data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def list_transactions(session: Session, organization_id: int | None = None) -> list[Transaction]:
    stmt = select(Transaction)
    if organization_id is not None:
        stmt = stmt.where(Transaction.organization_id == organization_id)
    return list(session.exec(stmt).all())


def get_financial_summary(session: Session, organization_id: int) -> dict[str, Any]:
    income = session.exec(
        select(func.sum(Transaction.amount)).where(
            Transaction.organization_id == organization_id,
            Transaction.type == "income",
        )
    ).first() or 0.0

    expenses = session.exec(
        select(func.sum(Transaction.amount)).where(
            Transaction.organization_id == organization_id,
            Transaction.type == "expense",
        )
    ).first() or 0.0

    budgets = list_budgets(session, organization_id)
    total_budget = sum(b.total for b in budgets)

    return {
        "organization_id": organization_id,
        "total_income": income,
        "total_expenses": expenses,
        "balance": income - expenses,
        "total_budget": total_budget,
        "budgets_count": len(budgets),
    }


def check_compliance(session: Session, organization_id: int) -> list[ComplianceCheck]:
    """Run a set of compliance rules and return findings."""
    results = []

    # Rule 1: Budget exceeded
    for budget in list_budgets(session, organization_id):
        status = get_budget_status(session, budget.id)
        if status and status["remaining"] < 0:
            results.append(
                ComplianceCheck(
                    organization_id=organization_id,
                    rule="budget_exceeded",
                    status="fail",
                    details=f"Budget '{budget.name}' exceeded by {abs(status['remaining'])} SAR",
                )
            )

    # Rule 2: Donation record without donor info (for amounts above 1000 SAR)
    stmt = select(Transaction).where(
        Transaction.organization_id == organization_id,
        Transaction.type == "income",
        Transaction.source == "donation",
        Transaction.amount > 1000,
    )
    for txn in session.exec(stmt).all():
        if not txn.donor_name:
            results.append(
                ComplianceCheck(
                    organization_id=organization_id,
                    rule="missing_donor_info",
                    status="warning",
                    details=f"Donation transaction {txn.id} (amount {txn.amount}) lacks donor name",
                )
            )

    # Rule 3: Basic financial transparency (warn if no income/expense records)
    tx_count = session.exec(
        select(func.count(Transaction.id)).where(
            Transaction.organization_id == organization_id
        )
    ).first() or 0
    if tx_count == 0:
        results.append(
            ComplianceCheck(
                organization_id=organization_id,
                rule="no_financial_records",
                status="warning",
                details="No financial transactions recorded; NCNP requires audited financial statements",
            )
        )

    # Rule 4: No budgets defined
    if not list_budgets(session, organization_id):
        results.append(
            ComplianceCheck(
                organization_id=organization_id,
                rule="no_budgets",
                status="warning",
                details="No budgets defined; governance requires annual budget",
            )
        )

    if not results:
        results.append(
            ComplianceCheck(
                organization_id=organization_id,
                rule="overall",
                status="pass",
                details="Basic compliance checks passed",
            )
        )

    session.add_all(results)
    session.commit()
    return results
