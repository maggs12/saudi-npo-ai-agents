import json
import re
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.core.config import settings


class LLMProvider:
    """Thin wrapper over available LLM backends."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.model = settings.openai_model
        self.ollama_model = settings.ollama_model
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if self.provider == "openai":
            from langchain_openai import ChatOpenAI

            self._client = ChatOpenAI(
                model=self.model,
                api_key=settings.openai_api_key,
                temperature=0.0,
            )
        elif self.provider == "ollama":
            from langchain_ollama import ChatOllama

            self._client = ChatOllama(
                base_url=settings.ollama_base_url,
                model=self.ollama_model,
                temperature=0.0,
            )
        else:
            from langchain_core.language_models.fake_chat_models import FakeListChatModel

            self._client = FakeListChatModel(
                responses=["مرحبًا، أنا وكيل المنصة غير الربحية."]
            )
        return self._client

    def _keyword_classify(self, text: str) -> dict[str, str]:
        text_lower = text.lower()
        # Map Arabic/English keywords to agents
        if any(k in text_lower for k in ["تقرير", "report", "pdf", "excel", "word", "إكسل", "وورد"]):
            return {"agent": "reporting", "intent": "report"}
        if any(k in text_lower for k in ["متطوع", "تطوع", "volunteer", "مهارة", "skill", "شهادة", "certificate", "ساعة"]):
            return {"agent": "volunteer", "intent": "volunteer"}
        if any(k in text_lower for k in [
            "مال", "موازنة", "ميزانية", "budget", "مصروف", "expense", "إيراد", "income",
            "تبرع", "donation", "زكاة", "ضريبة", "tax", "امتثال", "compliance",
            "حوكمة", "governance", "ncnp", "zatca", "pdpl", "socpa", "لائحة", "لوائح",
            "قانون", "نظام", "regulation", "مخالفة", "مخاطر",
        ]):
            return {"agent": "governance", "intent": "finance"}
        if any(k in text_lower for k in ["برنامج", "برامج", "program", "مشروع", "project", "هدف", "goal", "kpi", "نشاط", "activity"]):
            return {"agent": "program", "intent": "program"}
        return {"agent": "general", "intent": "general"}

    def classify(self, text: str) -> dict[str, str]:
        if self.provider == "mock":
            return self._keyword_classify(text)

        # For paid LLM providers, we can use a structured prompt; fallback to keyword on error.
        client = self._get_client()
        prompt = (
            "أنت مصنف نية عربي. حدد الوكيل الأنسب لهذا الطلب من الخيارات: "
            "program, volunteer, governance, reporting, general. "
            "أعد JSON فقط: {\"agent\": \"...\", \"intent\": \"...\"}.\n"
            f"النص: {text}"
        )
        try:
            messages = [SystemMessage(content="مصنف نية"), HumanMessage(content=prompt)]
            response = client.invoke(messages)
            content = response.content if isinstance(response, AIMessage) else str(response)
            match = re.search(r"\{.*?\}", content)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return self._keyword_classify(text)

    def generate_response(self, messages: list[BaseMessage]) -> str:
        if self.provider == "mock":
            # Return the last AI content or a generic message in Arabic
            for m in reversed(messages):
                if isinstance(m, AIMessage):
                    return str(m.content)
            return "تم تنفيذ طلبك."

        client = self._get_client()
        try:
            response = client.invoke(messages)
            return str(response.content)
        except Exception:
            return "حدث خطأ أثناء الاتصال بنموذج اللغة. يرجى التحقق من إعدادات LLM."


class EmbeddingProvider:
    """Wrapper over embedding backends."""

    def __init__(self) -> None:
        self.provider = settings.embedding_provider
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if self.provider == "openai":
            from langchain_openai import OpenAIEmbeddings

            self._client = OpenAIEmbeddings(
                model=self.model,
                api_key=settings.openai_api_key,
            )
        elif self.provider == "fastembed":
            try:
                from fastembed import TextEmbedding

                self._client = TextEmbedding(model_name=self.model)
            except Exception as exc:
                raise RuntimeError(f"Failed to load fastembed model: {exc}")
        else:
            self._client = None
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        if client is None:
            # deterministic mock embedding
            import hashlib

            return [
                [
                    ((int(hashlib.md5(f"{t}_{i}".encode()).hexdigest(), 16) % 10000) / 10000.0)
                    for i in range(self.dimension)
                ]
                for t in texts
            ]

        if self.provider == "openai":
            return client.embed_documents(texts)

        # fastembed
        return [list(embedding) for embedding in client.embed(texts)]


llm_provider = LLMProvider()
embedding_provider = EmbeddingProvider()
