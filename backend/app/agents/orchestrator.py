from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.agents.governance_agent import governance_agent
from app.agents.program_agent import program_agent
from app.agents.reporting_agent import reporting_agent
from app.agents.volunteer_agent import volunteer_agent
from app.core.providers import llm_provider


class OrchestratorState(TypedDict, total=False):
    messages: list[Any]
    intent: str
    agent_name: str
    tool_result: dict[str, Any]
    response: str


class Orchestrator:
    """LangGraph-based router that dispatches user requests to the right agent."""

    def __init__(self, session):
        self.session = session
        self.agents = {
            "program": program_agent,
            "volunteer": volunteer_agent,
            "governance": governance_agent,
            "reporting": reporting_agent,
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(OrchestratorState)
        builder.add_node("classify", self._classify_node)
        builder.add_node("dispatch", self._dispatch_node)
        builder.add_node("final", self._final_node)

        builder.add_edge(START, "classify")
        builder.add_edge("classify", "dispatch")
        builder.add_edge("dispatch", "final")
        builder.add_edge("final", END)

        return builder.compile()

    def _classify_node(self, state: OrchestratorState) -> OrchestratorState:
        # Last human message
        user_message = ""
        for m in reversed(state["messages"]):
            if isinstance(m, HumanMessage):
                user_message = str(m.content)
                break

        result = llm_provider.classify(user_message)
        return {
            **state,
            "intent": result.get("intent", "general"),
            "agent_name": result.get("agent", "general"),
        }

    def _dispatch_node(self, state: OrchestratorState) -> OrchestratorState:
        agent_name = state.get("agent_name", "general")
        user_message = ""
        for m in reversed(state["messages"]):
            if isinstance(m, HumanMessage):
                user_message = str(m.content)
                break

        if agent_name == "general" or agent_name not in self.agents:
            tool_result = {
                "agent": "general",
                "message": "أهلاً بك في منصة وكلاء الذكاء الاصطناعي للقطاع غير الربحي. يمكنك سؤالي عن البرامج، المتطوعين، الحوكمة والمالية، أو التقارير.",
            }
        else:
            tool_result = self.agents[agent_name].run(self.session, user_message)

        return {**state, "tool_result": tool_result}

    def _final_node(self, state: OrchestratorState) -> OrchestratorState:
        tool_result = state.get("tool_result", {})
        agent_name = tool_result.get("agent", state.get("agent_name", "general"))

        if agent_name in self.agents:
            final = self.agents[agent_name].final_message(tool_result)
        else:
            final = tool_result.get("message", "تم استلام طلبك.")

        # If LLM provider is not mock, we can ask it to polish the final message.
        # For simplicity and reliability, we use the agent's final_message.
        return {**state, "response": final}

    def invoke(self, message: str, thread_id: str | None = None, user_id: str | None = None) -> dict[str, Any]:
        state = {
            "messages": [SystemMessage(content="أنت مساعد ذكي للقطاع غير الربحي في السعودية."), HumanMessage(content=message)],
            "intent": "",
            "agent_name": "",
            "tool_result": {},
            "response": "",
        }
        result = self.graph.invoke(state)
        return {
            "agent": result.get("agent_name", "general"),
            "intent": result.get("intent", ""),
            "response": result.get("response", ""),
            "tool_result": result.get("tool_result", {}),
        }


def get_orchestrator(session) -> Orchestrator:
    return Orchestrator(session)
