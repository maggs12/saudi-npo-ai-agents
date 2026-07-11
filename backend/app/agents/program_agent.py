import re
from typing import Any

from app.services.program_service import (
    add_activity,
    add_kpi,
    create_program,
    get_program_status,
    list_programs,
    update_activity,
    update_kpi,
    update_program,
)


class ProgramAgent:
    name = "program"
    system_prompt = (
        "أنت وكيل إدارة البرامج في جمعية خيرية سعودية. "
        "مهمتك تصميم وتتبع البرامج والمشاريع الخيرية (أهداف، مؤشرات KPI، أنشطة)."
    )

    def run(self, session, message: str) -> dict[str, Any]:
        text = message.lower()

        if any(k in text for k in ["قائمة", "list", "كل", "جميع"]):
            return self.run_direct(session, {"action": "list"})

        if any(k in text for k in ["حالة", "status", "تقدم", "progress"]):
            # Try to find program id
            match = re.search(r"\d+", message)
            program_id = int(match.group()) if match else None
            return self.run_direct(session, {"action": "status", "program_id": program_id})

        if any(k in text for k in ["أنشئ", "create", "أضف", "add", "جديد"]):
            # Try to extract program name after the keyword
            name = self._extract_name(message)
            return self.run_direct(
                session,
                {"action": "create", "data": {"name": name, "organization_id": 1}},
            )

        if any(k in text for k in ["نشاط", "activity"]):
            match = re.search(r"\d+", message)
            program_id = int(match.group()) if match else None
            return self.run_direct(
                session,
                {"action": "add_activity", "program_id": program_id, "data": {"name": "نشاط جديد"}},
            )

        if any(k in text for k in ["kpi", "مؤشر", "أداء"]):
            match = re.search(r"\d+", message)
            program_id = int(match.group()) if match else None
            return self.run_direct(
                session,
                {"action": "add_kpi", "program_id": program_id, "data": {"name": "مؤشر أداء"}},
            )

        return self.run_direct(session, {"action": "list"})

    def _extract_name(self, message: str) -> str:
        # crude extraction: get text after "برنامج" or "program" or "اسم"
        for keyword in ["برنامج", "program", "اسم"]:
            if keyword in message:
                parts = message.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip().strip("\"'؟!.")
        return "برنامج جديد"

    def run_direct(self, session, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "list")
        data = payload.get("data", {})
        program_id = payload.get("program_id")

        if action == "create":
            program = create_program(session, data)
            return {"agent": self.name, "action": "create", "program": program.model_dump()}

        if action == "list":
            organization_id = payload.get("organization_id")
            programs = list_programs(session, organization_id)
            return {
                "agent": self.name,
                "action": "list",
                "programs": [p.model_dump() for p in programs],
            }

        if action == "status":
            if program_id is None:
                return {"agent": self.name, "error": "program_id is required"}
            status = get_program_status(session, program_id)
            return {"agent": self.name, "action": "status", "status": status}

        if action == "add_activity":
            if program_id is None:
                return {"agent": self.name, "error": "program_id is required"}
            activity = add_activity(session, program_id, data)
            return {"agent": self.name, "action": "add_activity", "activity": activity.model_dump()}

        if action == "add_kpi":
            if program_id is None:
                return {"agent": self.name, "error": "program_id is required"}
            kpi = add_kpi(session, program_id, data)
            return {"agent": self.name, "action": "add_kpi", "kpi": kpi.model_dump()}

        if action == "update_kpi":
            kpi_id = payload.get("kpi_id")
            actual_value = payload.get("actual_value")
            if kpi_id is None or actual_value is None:
                return {"agent": self.name, "error": "kpi_id and actual_value required"}
            kpi = update_kpi(session, kpi_id, actual_value)
            return {"agent": self.name, "action": "update_kpi", "kpi": kpi.model_dump() if kpi else None}

        if action == "update_activity":
            activity_id = payload.get("activity_id")
            if activity_id is None:
                return {"agent": self.name, "error": "activity_id is required"}
            activity = update_activity(session, activity_id, data)
            return {"agent": self.name, "action": "update_activity", "activity": activity.model_dump() if activity else None}

        if action == "update":
            if program_id is None:
                return {"agent": self.name, "error": "program_id is required"}
            program = update_program(session, program_id, data)
            return {"agent": self.name, "action": "update", "program": program.model_dump() if program else None}

        return {"agent": self.name, "error": "unknown action"}

    def final_message(self, result: dict[str, Any]) -> str:
        if "error" in result:
            return f"خطأ في وكيل البرامج: {result['error']}"
        if result.get("action") == "create":
            p = result.get("program", {})
            return f"تم إنشاء البرنامج '{p.get('name')}' بنجاح."
        if result.get("action") == "list":
            count = len(result.get("programs", []))
            return f"يوجد {count} برنامج/برامج مسجلة."
        if result.get("action") == "status":
            s = result.get("status", {})
            return (
                f"حالة البرنامج '{s.get('name')}': {s.get('status')} - "
                f"التقدم الكلي {s.get('overall_progress')}%"
            )
        return "تم تنفيذ العملية على وكيل البرامج."


program_agent = ProgramAgent()
