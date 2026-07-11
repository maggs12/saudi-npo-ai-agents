import pytest
from sqlmodel import Session

from app.agents.orchestrator import Orchestrator


@pytest.fixture
def orchestrator(db_session: Session):
    return Orchestrator(db_session)


@pytest.mark.parametrize(
    "message,expected_agent",
    [
        ("أريد إنشاء برنامج جديد", "program"),
        ("أضف نشاط للبرنامج 1", "program"),
        ("قائمة المتطوعين", "volunteer"),
        ("سجل متطوع جديد", "volunteer"),
        ("كم ساعات التطوع للمتطوع 1؟", "volunteer"),
        ("ما حالة الميزانية؟", "governance"),
        ("افحص الامتثال", "governance"),
        ("ما إجمالي الإيرادات؟", "governance"),
        ("اطلعني على آخر لائحة NCNP", "governance"),
        ("أريد تقرير PDF شهري", "reporting"),
        ("generate annual report excel", "reporting"),
        ("السلام عليكم", "general"),
    ],
)
def test_orchestrator_routing(orchestrator: Orchestrator, message: str, expected_agent: str):
    result = orchestrator.invoke(message)
    assert result["agent"] == expected_agent
    assert result["response"]


def test_orchestrator_accuracy_metric(orchestrator: Orchestrator):
    """Documented accuracy metric: 90% test cases should route correctly."""
    cases = [
        ("إنشاء برنامج", "program"),
        ("تسجيل متطوع", "volunteer"),
        ("تقرير", "reporting"),
        ("موازنة", "governance"),
        ("hello", "general"),
        ("قائمة البرامج", "program"),
        ("فرص تطوع", "volunteer"),
        ("فحص الامتثال", "governance"),
        ("تقرير سنوي", "reporting"),
        ("شكراً", "general"),
    ]
    correct = 0
    for message, expected in cases:
        result = orchestrator.invoke(message)
        if result["agent"] == expected:
            correct += 1
    accuracy = correct / len(cases)
    assert accuracy >= 0.9, f"Orchestrator accuracy {accuracy} below 0.9"
