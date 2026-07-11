from typing import Any

from app.services.finance_service import check_compliance, get_financial_summary, list_budgets
from app.services.regulation_service import search_regulations_with_fallback
from app.tools.web_search import web_search


class GovernanceAgent:
    name = "governance"
    system_prompt = (
        "أنت وكيل الحوكمة والمالية في جمعية خيرية سعودية. "
        "مهمتك إدارة الموازنات والمصروفات والإيرادات، وإجراء فحوصات الامتثال لـ NCNP وZATCA."
    )

    def run(self, session, message: str) -> dict[str, Any]:
        text = message.lower()
        if any(k in text for k in ["موازنة", "budget", "budgets"]):
            return self.run_direct(session, {"action": "list_budgets"})

        if any(k in text for k in ["مال", "finance", "مالي", "summary", "ملخص"]):
            return self.run_direct(session, {"action": "financial_summary"})

        if any(k in text for k in ["امتثال", "compliance", "مخالفة", "risk", "مخاطر"]):
            return self.run_direct(session, {"action": "check_compliance"})

        if any(k in text for k in ["لائحة", "regulation", "قانون", "نظام", "ncnp", "zatca", "pdpl"]):
            return self.run_direct(session, {"action": "search_regulations", "query": message})

        return self.run_direct(session, {"action": "financial_summary"})

    def run_direct(self, session, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "financial_summary")
        organization_id = payload.get("organization_id", 1)

        if action == "list_budgets":
            budgets = list_budgets(session, organization_id)
            return {
                "agent": self.name,
                "action": "list_budgets",
                "budgets": [b.model_dump() for b in budgets],
            }

        if action == "financial_summary":
            summary = get_financial_summary(session, organization_id)
            return {"agent": self.name, "action": "financial_summary", "summary": summary}

        if action == "check_compliance":
            results = check_compliance(session, organization_id)
            return {
                "agent": self.name,
                "action": "check_compliance",
                "checks": [c.model_dump() for c in results],
            }

        if action == "search_regulations":
            query = payload.get("query", "NCNP non-profit governance rules")
            # First use web search to ensure fresh data and citations
            web_results = web_search(query, max_results=3)
            # Then search local vector store
            local_results = search_regulations_with_fallback(session, query, top_k=3)
            return {
                "agent": self.name,
                "action": "search_regulations",
                "query": query,
                "web_results": web_results,
                "local_results": local_results,
            }

        return {"agent": self.name, "error": "unknown action"}

    def final_message(self, result: dict[str, Any]) -> str:
        if "error" in result:
            return f"خطأ في وكيل الحوكمة: {result['error']}"
        if result.get("action") == "financial_summary":
            s = result.get("summary", {})
            return (
                f"الإيرادات: {s.get('total_income', 0):,.2f} ريال، "
                f"المصروفات: {s.get('total_expenses', 0):,.2f} ريال، "
                f"الرصيد: {s.get('balance', 0):,.2f} ريال."
            )
        if result.get("action") == "check_compliance":
            checks = result.get("checks", [])
            failures = [c for c in checks if c.get("status") in ("fail", "warning")]
            if not failures:
                return "جميع فحوصات الامتثال الأساسية ناجحة."
            return f"تم العثور على {len(failures)} ملاحظة/ملاحظات امتثال."
        if result.get("action") == "search_regulations":
            web = result.get("web_results", [])
            local = result.get("local_results", [])
            sources = [r.get("url", "") for r in web if r.get("url")]
            source_text = "، ".join(sources[:2])
            return f"تم استرجاع {len(local)} وثيقة من المخزن المحلي و{len(web)} نتيجة من الويب. المصادر: {source_text}"
        return "تم تنفيذ العملية على وكيل الحوكمة."


governance_agent = GovernanceAgent()
