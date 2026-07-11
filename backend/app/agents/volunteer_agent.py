import re
from datetime import date
from typing import Any

from app.services.volunteer_service import (
    create_opportunity,
    create_volunteer,
    get_total_hours,
    get_volunteer,
    issue_certificate,
    list_opportunities,
    list_volunteers,
    log_hours,
    match_volunteers,
    register_volunteer,
)


class VolunteerAgent:
    name = "volunteer"
    system_prompt = (
        "أنت وكيل إدارة التطوع في جمعية خيرية سعودية. "
        "مهمتك تسجيل المتطوعين، مطابقة مهاراتهم مع الفرص، وتوثيق الساعات وإصدار الشهادات."
    )

    def run(self, session, message: str) -> dict[str, Any]:
        text = message.lower()
        if any(k in text for k in ["قائمة", "list", "كل", "المتطوعين"]):
            return self.run_direct(session, {"action": "list"})

        if any(k in text for k in ["match", "مطابقة", "مناسب", "مهارة"]):
            match = re.search(r"\d+", message)
            opp_id = int(match.group()) if match else None
            return self.run_direct(session, {"action": "match", "opportunity_id": opp_id})

        if any(k in text for k in ["ساعات", "hours", "توثيق"]):
            match = re.search(r"\d+", message)
            volunteer_id = int(match.group()) if match else None
            return self.run_direct(session, {"action": "total_hours", "volunteer_id": volunteer_id})

        if any(k in text for k in ["شهادة", "certificate"]):
            numbers = re.findall(r"\d+", message)
            if len(numbers) >= 2:
                volunteer_id, opportunity_id = int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                volunteer_id = int(numbers[0])
                opportunity_id = None
            else:
                volunteer_id = opportunity_id = None
            return self.run_direct(
                session,
                {"action": "issue_certificate", "volunteer_id": volunteer_id, "opportunity_id": opportunity_id},
            )

        if any(k in text for k in ["فرصة", "opportunity", "فرص"]):
            return self.run_direct(session, {"action": "list_opportunities"})

        if any(k in text for k in ["أنشئ", "create", "تسجيل", "register"]):
            return self.run_direct(session, {"action": "create", "data": {"name": "متطوع جديد"}})

        return self.run_direct(session, {"action": "list"})

    def run_direct(self, session, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "list")
        data = payload.get("data", {})

        if action == "create":
            volunteer = create_volunteer(session, data)
            return {"agent": self.name, "action": "create", "volunteer": volunteer.model_dump()}

        if action == "list":
            volunteers = list_volunteers(session)
            return {"agent": self.name, "action": "list", "volunteers": [v.model_dump() for v in volunteers]}

        if action == "list_opportunities":
            organization_id = payload.get("organization_id")
            opportunities = list_opportunities(session, organization_id=organization_id)
            return {
                "agent": self.name,
                "action": "list_opportunities",
                "opportunities": [o.model_dump() for o in opportunities],
            }

        if action == "match":
            opportunity_id = payload.get("opportunity_id")
            if opportunity_id is None:
                return {"agent": self.name, "error": "opportunity_id is required"}
            matches = match_volunteers(session, opportunity_id)
            return {"agent": self.name, "action": "match", "matches": matches}

        if action == "register":
            volunteer_id = payload.get("volunteer_id")
            opportunity_id = payload.get("opportunity_id")
            if volunteer_id is None or opportunity_id is None:
                return {"agent": self.name, "error": "volunteer_id and opportunity_id required"}
            enrollment = register_volunteer(session, volunteer_id, opportunity_id)
            return {"agent": self.name, "action": "register", "enrollment": enrollment.model_dump()}

        if action == "log_hours":
            record_data = {
                "volunteer_id": payload.get("volunteer_id"),
                "opportunity_id": payload.get("opportunity_id"),
                "hours_date": payload.get("hours_date", date.today()),
                "hours": payload.get("hours", 0),
                "description": payload.get("description"),
            }
            record = log_hours(session, record_data)
            return {"agent": self.name, "action": "log_hours", "record": record.model_dump()}

        if action == "total_hours":
            volunteer_id = payload.get("volunteer_id")
            if volunteer_id is None:
                return {"agent": self.name, "error": "volunteer_id is required"}
            total = get_total_hours(session, volunteer_id)
            return {"agent": self.name, "action": "total_hours", "total_hours": total}

        if action == "issue_certificate":
            volunteer_id = payload.get("volunteer_id")
            opportunity_id = payload.get("opportunity_id")
            if volunteer_id is None or opportunity_id is None:
                return {"agent": self.name, "error": "volunteer_id and opportunity_id required"}
            cert = issue_certificate(session, volunteer_id, opportunity_id)
            return {"agent": self.name, "action": "issue_certificate", "certificate": cert}

        return {"agent": self.name, "error": "unknown action"}

    def final_message(self, result: dict[str, Any]) -> str:
        if "error" in result:
            return f"خطأ في وكيل التطوع: {result['error']}"
        if result.get("action") == "create":
            v = result.get("volunteer", {})
            return f"تم تسجيل المتطوع '{v.get('name')}' بنجاح."
        if result.get("action") == "list":
            count = len(result.get("volunteers", []))
            return f"يوجد {count} متطوع/متطوعين."
        if result.get("action") == "match":
            count = len(result.get("matches", []))
            return f"تم العثور على {count} متطوع مطابق للفرصة."
        if result.get("action") == "total_hours":
            return f"إجمالي الساعات التطوعية: {result.get('total_hours', 0)} ساعة."
        return "تم تنفيذ العملية على وكيل التطوع."


volunteer_agent = VolunteerAgent()
