# منصة وكلاء الذكاء الاصطناعي للقطاع غير الربحي في السعودية

منصة Multi-Agent AI متكاملة لإدارة الجمعيات والمؤسسات غير الربحية السعودية، مع التوافق التنظيمي مع المركز الوطني لتنمية القطاع غير الربحي (NCNP)، هيئة الزكاة والضريبة والجمارك (ZATCA)، الهيئة السعودية للمراجعين والمحاسبين (SOCPA)، ونظام حماية البيانات الشخصية (PDPL).

## المميزات الرئيسية

- **أربعة وكلاء متخصصون:**
  - وكيل إدارة البرامج (Program Management Agent)
  - وكيل إدارة التطوع (Volunteer Management Agent)
  - وكيل الحوكمة والمالية (Governance & Finance Agent)
  - وكيل كتابة التقارير (Reporting Agent)
- **Orchestrator** يوجّه الطلبات تلقائيًا إلى الوكيل المناسب.
- **واجهة ويب RTL** بالعربية باستخدام Next.js و Tailwind CSS.
- **قاعدة بيانات موحدة** PostgreSQL + pgvector.
- **RAG** لاسترجاع الوثائق التنظيمية وتحديثها من الويب.
- **توليد تقارير عربية RTL** بصيغ PDF و Word و Excel.
- **امتثال PDPL** عبر تشفير الأعمدة الحساسة وسجل audit_logs.
- **اختبارات وحدة وتكامل** 100%.
- **تشغيل بنقرة واحدة** عبر Docker Compose.

## المتطلبات

- Docker و Docker Compose
- (اختياري) Python 3.10+ و Node.js 20+ للتطوير المحلي

## التشغيل

1. انسخ ملف البيئة:

```bash
cp .env.example .env
```

2. ابدأ كل الخدمات:

```bash
docker compose up --build
```

3. افتح المتصفح:

- الواجهة الأمامية: http://localhost:3000
- واجهة برمجة التطبيقات: http://localhost:8000
- مستندات API: http://localhost:8000/docs

## إعدادات البيئة

انظر `.env.example`. الأهم:

- `DATABASE_URL`: عنوان قاعدة البيانات.
- `SECRET_KEY` و `ENCRYPTION_KEY`: مفاتيح التوقيع والتشفير.
- `API_KEY`: مفتاح مشترك (shared secret) لحماية جميع مسارات `/api/v1` (ما عدا `/health`).
- `LLM_PROVIDER`: `openai` | `ollama` | `mock`.
- `EMBEDDING_PROVIDER`: `openai` | `fastembed` | `mock`.
- `OPENAI_API_KEY`: عند استخدام OpenAI.

## الاختبارات

### محليًا

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

### داخل Docker

```bash
docker compose exec -e DATABASE_URL=postgresql://postgres:postgres@db:5432/npo_ai_test backend pytest -v
```

## الوكلاء والـ API

- `POST /api/v1/chat` – شات موحّد مع الـ Orchestrator.
- `POST /api/v1/agents/{agent_name}/run` – استدعاء مباشر لوكيل.
- `GET /api/v1/dashboard` – لوحة تحكم موحدة.
- `POST /api/v1/reports` – توليد تقرير.
- `GET /api/v1/reports/{id}/download` – تحميل التقرير.
- `POST /api/v1/compliance/check` – فحص الامتثال.
- `POST /api/v1/regulations/search` – بحث RAG في اللوائح.

## التوسعة

لإضافة وكيل جديد:

1. أنشئ صفًا جديدًا في `backend/app/agents/`.
2. أضفه إلى `backend/app/agents/orchestrator.py`.
3. أضف نقاط API في `backend/app/api/v1.py`.
4. أضف اختبارات في `backend/tests/`.

## التوثيق

- `docs/SOURCES.md` – المصادر التنظيمية والتقنية.
- `docs/regulatory-context.md` – السياق التنظيمي السعودي.
- `docs/decisions.md` – سجل القرارات التقنية.
- `docs/architecture.md` – بنية النظام.

## المساهمون

تم تطوير المشروع من قبل المستخدم ماجد بمساعدة Devin.
