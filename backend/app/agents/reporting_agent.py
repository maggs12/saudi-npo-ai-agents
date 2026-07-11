from datetime import date
from typing import Any

from app.models import Report
from app.services.reporting_service import build_program_dashboard, build_volunteer_summary, generate_report
from app.services.finance_service import get_financial_summary


class ReportingAgent:
    name = "reporting"
    system_prompt = (
        "أنت وكيل كتابة التقارير في جمعية خيرية سعودية. "
        "مهمتك توليد تقارير دورية (شهرية/ربع سنوية/سنوية/لـ NCNP) بصيغ PDF وWord وExcel."
    )

    def run(self, session, message: str) -> dict[str, Any]:
        text = message.lower()
        fmt = "pdf"
        if any(k in text for k in ["word", "docx", "وورد"]):
            fmt = "word"
        elif any(k in text for k in ["excel", "إكسل", "xlsx"]):
            fmt = "excel"

        report_type = "monthly"
        if any(k in text for k in ["سنوي", "annual", "سنوية"]):
            report_type = "annual"
        elif any(k in text for k in ["ربع", "quarter", "quarterly"]):
            report_type = "quarterly"
        elif any(k in text for k in ["ncnp", "حكومي", "رسمي"]):
            report_type = "ncnp"

        period = date.today().strftime("%Y-%m")
        import re
        match = re.search(r"\d{4}[-/]\d{1,2}", message)
        if match:
            period = match.group().replace("/", "-")

        return self.run_direct(
            session,
            {
                "action": "generate",
                "organization_id": 1,
                "report_type": report_type,
                "period": period,
                "format": fmt,
            },
        )

    def run_direct(self, session, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "generate")
        organization_id = payload.get("organization_id", 1)

        if action == "dashboard":
            return {
                "agent": self.name,
                "action": "dashboard",
                "programs": build_program_dashboard(session, organization_id),
                "volunteers": build_volunteer_summary(session, organization_id),
                "finance": get_financial_summary(session, organization_id),
            }

        if action == "generate":
            report_type = payload.get("report_type", "monthly")
            period = payload.get("period", date.today().strftime("%Y-%m"))
            fmt = payload.get("format", "pdf")
            report = generate_report(session, organization_id, report_type, period, fmt)
            return {
                "agent": self.name,
                "action": "generate",
                "report": report.model_dump(),
                "file_path": report.file_path,
                "download_url": f"/api/v1/reports/{report.id}/download",
            }

        return {"agent": self.name, "error": "unknown action"}

    def final_message(self, result: dict[str, Any]) -> str:
        if "error" in result:
            return f"خطأ في وكيل التقارير: {result['error']}"
        if result.get("action") == "generate":
            report = result.get("report", {})
            return (
                f"تم توليد التقرير '{report.get('report_type')}' للفترة {report.get('period')} بنجاح. "
                f"يمكنك تحميله من {result.get('download_url', '')}"
            )
        return "تم تنفيذ العملية على وكيل التقارير."


reporting_agent = ReportingAgent()
