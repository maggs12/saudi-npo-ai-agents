# العمارة التقنية للمنصة

## 1. المكونات الرئيسية

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User / Web Browser                            │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │ HTTPS / HTTP
┌─────────────────────────────────────▼───────────────────────────────┐
│                    Next.js Frontend (RTL)                           │
│  - Unified chat interface                                           │
│  - Dashboard for four agents                                        │
│  - Report download (PDF/Word/Excel)                                 │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │ REST API / JSON
┌─────────────────────────────────────▼───────────────────────────────┐
│                   FastAPI Backend (Python)                          │
│  - /api/v1/chat          -> Orchestrator (LangGraph)                │
│  - /api/v1/agents/{name} -> Direct agent invocation                 │
│  - /api/v1/reports       -> Report generation                       │
│  - /api/v1/seed          -> Seed data                               │
│  - /health               -> Health check                            │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │ SQLAlchemy / psycopg2
┌─────────────────────────────────────▼───────────────────────────────┐
│              PostgreSQL + pgvector (vector store)                   │
│  - Programs, Volunteers, Transactions, Reports, Regulations         │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Orchestrator Router (LangGraph)

- يُستخدم `langgraph.StateGraph` لإدارة حالة المحادثة والتوجيه.
- الحالة `OrchestratorState` تتضمن:
  - `messages`: قائمة الرسائل (Human/AI/System).
  - `intent`: النية المستخرجة.
  - `agent_name`: الوكيل المستهدف.
  - `context`: سياق المستخدم (thread_id, user_id).
  - `tool_calls`: المكالمات التي قام بها الوكيل.
  - `response`: الرد النهائي.
- عقد التوجيه:
  - `classify`: يحدد النية (برنامج، تطوع، حوكمة، تقرير، عام).
  - `dispatch`: يستدعي الوكيل المناسب.
  - `combine` (اختياري): يجمع بيانات من أكثر من وكيل إذا كان الطلب تقريرًا.
  - `final`: يُنتج الرد النهائي بالعربية.
- يدعم checkpointing عبر `PostgresSaver` (إعداد اختياري) لاستمرار حالة المحادثة.

## 3. الوكلاء الأربعة

كل وكيل عبارة عن وحدة Python منفصلة تحتوي على:

- `system_prompt`: تعليمات بالعربية الفصحى.
- `tools`: أدوات CRUD على قاعدة البيانات + أدوات خارجية.
- `self_check`: منطق التحقق الذاتي قبل إرجاع النتيجة.
- `run(payload)` / `invoke(state)`: نقطة الدخول.

### 3.1 Program Management Agent
- إدارة البرامج والمشاريع الخيرية.
- أدوات: `create_program`, `list_programs`, `get_program`, `update_program`, `add_activity`, `update_kpi`, `get_program_status`.
- حساب حالة البرنامج: منجز / متأخر / متعطل بناءً على المؤشرات والأنشطة.

### 3.2 Volunteer Management Agent
- تسجيل المتطوعين، المهارات، الفرص، الجدولة، الشهادات.
- أدوات: `register_volunteer`, `match_volunteer`, `schedule_volunteer`, `log_hours`, `issue_certificate`, `get_volunteer_hours`.
- التكامل مع منصة تطوع: placeholder API client يدعم CSV/JSON + webhook.

### 3.3 Governance & Finance Agent
- الموازنات، المصروفات، الإيرادات، الامتثال.
- أدوات: `create_budget`, `record_income`, `record_expense`, `get_budget_status`, `check_compliance`, `search_regulations`, `web_search`.
- RAG: مخزن `regulations` في `pgvector` يُغذى بالنتائج من `duckduckgo-search`.
- تنبيهات الامتثال: تجاوز الموازنة، فقدان المستندات، مخالفة PDPL.

### 3.4 Reporting Agent
- توليد التقارير الدورية والمخصصة.
- أدوات: `generate_report`, `generate_ncnp_report`, `generate_program_dashboard`, `get_financial_summary`, `get_volunteer_summary`, `export_pdf`, `export_word`, `export_excel`.
- يجمع بيانات الوكلاء الآخرين من قاعدة البيانات.
- يستخدم `fpdf2` + `python-docx` + `openpyxl` للإخراج.
- تصميم RTL عربي مع دعم شعار الجمعية.

## 4. قاعدة البيانات

استخدمنا **PostgreSQL** (صورة `pgvector/pgvector:pg16`) لما يلي:

- دعم العلاقات المعقدة بين البرامج والمتطوعين والمالية.
- `pgvector` لمتجر المتجهات.
- ACID compliance للبيانات المالية.
- jsonb لمرونة البيانات المستقبلية.

### الجداول الرئيسية
- `organizations`
- `programs`
- `activities`
- `kpis`
- `volunteers`
- `skills`
- `volunteer_opportunities`
- `volunteer_hours`
- `budgets`
- `transactions`
- `reports`
- `regulations` (مع عمود `vector` لـ pgvector)
- `audit_logs` (لـ PDPL RoPA)
- `conversations` (ذاكرة المحادثة)

## 5. الأمان والامتثال

- تشفير كلمات المرور بـ `bcrypt`.
- TLS داخل Docker عبر `traefik` أو `caddy` (اختياري)؛ في الإعداد الأولي يستخدم HTTP داخل الشبكة الداخلية.
- تشفير الأعمدة الحساسة (بطاقات الهوية، هواتف المتطوعين، بيانات المتبرعين) عند الحاجة.
- تسجيل `audit_logs` لكل عملية تغيير على البيانات الشخصية.
- `.env` لإدارة الأسرار وعدم تضمينها في الكود.

## 6. LLM واختيار النموذج

- `LLM_PROVIDER` يدعم: `openai`, `ollama`, `mock`.
- `mock` يستخدم `langchain_core` `FakeListChatModel` للاختبارات.
- `EMBEDDING_PROVIDER` يدعم: `openai`, `fastembed`, `mock`.
- يمكن للمستخدم إدخال `OPENAI_API_KEY` أو `OLLAMA_BASE_URL` في `.env`.

## 7. الاختبارات

- `pytest` للواجهة الخلفية.
- اختبارات وحدة لكل وكيل.
- اختبارات تكامل للـ API.
- اختبار دقة التوجيه (routing accuracy) للـ Orchestrator.
- اختبارات RAG وتوليد التقارير.
