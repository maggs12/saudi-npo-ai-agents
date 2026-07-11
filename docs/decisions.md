# سجل القرارات التقنية (Decision Log)

## 1. إطار العمل Multi-Agent

**القرار:** استخدام **LangGraph** لبناء الـ Orchestrator.

**الأسباب:**
- يوفر تحكمًا صريحًا في حالة العمل (state graph) وconditional edges.
- يدعم checkpointing واستمرار الحالة لمحادثات طويلة.
- يدعم human-in-the-loop عند الحاجة.
- بحث 2026 يرشح LangGraph للأنظمة الإنتاجية طويلة الأمد، بينما CrewAI أسرع للنماذج الأولية وAutoGen في وضع الصيانة.
- الالتزام بالطلبة (prompts) والأدوات بالعربية ممكن دون تقيد إضافي من الإطار.

**البدائل:**
- CrewAI: جيد للنماذج السريعة لكن أقل مرونة في التوجيه الدقيق.
- Microsoft Agent Framework: يتطلب .NET/Azure إضافي.

## 2. قاعدة البيانات

**القرار:** استخدام **PostgreSQL** مع امتداد **pgvector**.

**الأسباب:**
- العلاقات بين البرامج والمتطوعين والمالية معقدة وتحتاج RDBMS.
- `pgvector` يوفر vector store داخل نفس قاعدة البيانات (لا حاجة لخدمة منفصلة).
- ACID compliance للبيانات المالية.
- دعم `jsonb` لاحتياجات مرنة مستقبلية.

**البدائل:**
- SQLite: سهل لكن لا يدعم pgvector ولا التزامن.
- Chroma: مخصص للمتجهات لكنه يضيف خدمة إضافية.

## 3. الـ Backend Framework

**القرار:** استخدام **FastAPI** مع **SQLModel**.

**الأسباب:**
- FastAPI سريع، يدعم async، ويولد OpenAPI/ Swagger تلقائيًا.
- SQLModel يجمع بين Pydantic وSQLAlchemy ويقلل التكرار.
- إنتاج واجهة REST موحدة للوكلاء.

## 4. إطار الواجهة الأمامية

**القرار:** استخدام **Next.js 14** مع **Tailwind CSS** ودعم RTL.

**الأسباب:**
- Next.js يوفر React SSR/SSG ودعم App Router.
- Tailwind يسرّع بناء واجهة RTL باستخدام `dir="rtl"`.
- يمكن التوسع إلى لوحة تحكم وشات موحد بسهولة.

## 5. LLM / Embeddings

**القرار:** دعم عدة مزودين عبر الإعدادات: `openai`, `ollama`, `mock` (افتراضي للاختبارات).

**الأسباب:**
- عدم وضع مفتاح API في الكود؛ المستخدم يضبط `.env`.
- `mock` يتيح تشغيل الاختبارات وعرض النظام بدون مفتاح خارجي.
- `ollama` يتيح تشغيل LLM محلي إن وجد.
- `openai` يوفر أداءً عاليًا عند توفر مفتاح.

**_embeddings:**
- `fastembed` لمتجهات محلية بدون مفتاح (نموذج `paraphrase-multilingual-MiniLM-L12V2`).
- `openai` للإنتاج.
- `mock` للاختبارات.

## 6. البحث على الويب (Web Search)

**القرار:** استخدام **duckduckgo-search** Python library.

**الأسباب:**
- لا تتطلب API key.
- كافية لجلب ملخصات المواقع والوثائق التنظيمية.
- يمكن استبدالها بـ `SerpAPI` أو `Tavily` لاحقًا.

## 7. توليد التقارير

**القرار:** استخدام **fpdf2** لـ PDF، **python-docx** لـ Word، **openpyxl** لـ Excel.

**الأسباب:**
- `fpdf2` يدعم TTF وUnicode ويمكن دمج `arabic-reshaper` و `python-bidi` لدعم العربية.
- `python-docx` و `openpyxl` خفيفة ومدعومة جيدًا.
- تجنب أدوات خارجية مثل `wkhtmltopdf` لتقليل التعقيد.

## 8. RAG للوثائق التنظيمية

**القرار:** `pgvector` + `fastembed` + `duckduckgo-search`.

**الأسباب:**
- `pgvector` يخزن المتجهات في نفس قاعدة البيانات.
- `fastembed` يولد متجهات بدون مفتاح.
- `duckduckgo-search` يجلب آخر التحديثات التنظيمية.
- `Governance Agent` يخزن ويسترجع الوثائق ويستشهد بالمصادر.

## 9. الأمان (PDPL)

**القرار:**
- إدارة الأسرار عبر `.env`.
- تشفير الأعمدة الحساسة في قاعدة البيانات (هواتف، بطاقات هوية، إيميلات المتبرعين والمتطوعين).
- `audit_logs` لكل عملية تغيير على بيانات شخصية.
- لا تخزين كلمات المرور في plain text.
- TLS داخل الإنتاج (اختياري في `docker-compose.yml` الأولي).

## 10. إدارة التبعيات والبناء

**القرار:**
- Python backend: `pyproject.toml` + `requirements.txt`.
- Frontend: `package.json` + `npm`.
- Docker: `docker compose` لرفع كامل النظام.
- `uv` / `pip` متاحان محليًا؛ Dockerfile يستخدم `pip` للاستقرار.

## 11. التكامل مع منصة تطوع

**القرار:** تصميم `VolunteerAgent` مع طبقة `TatawwaClient` placeholder.

**الأسباب:**
- البحث لم يثبت توفر API عام للمنصة الوطنية للعمل التطوعي.
- يمكن التكامل لاحقًا عند توفر API رسمي أو عبر تصدير/استيراد CSV/JSON.
- التصميم المعياري يسهل إضافة الـ adapter.
