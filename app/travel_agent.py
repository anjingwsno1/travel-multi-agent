import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.model import create_chat_model
from tools import generate_image, get_weather


class TravelAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


DEFAULT_TOOLS = [get_weather, generate_image]


def build_travel_agent(model=None, tools: list[BaseTool] | None = None):
    """Build a single-agent graph that can call travel tools until it has an answer."""
    active_tools = tools or DEFAULT_TOOLS
    bound_model = (model or create_chat_model()).bind_tools(active_tools)

    def call_model(state: TravelAgentState):
        response = bound_model.invoke(state["messages"])
        return {"messages": [response]}

    def route_after_model(state: TravelAgentState):
        latest_message = state["messages"][-1]
        if isinstance(latest_message, AIMessage) and latest_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(TravelAgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(active_tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", route_after_model, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    return workflow.compile()


def run_travel_agent(query: str) -> str:
    """Run the travel agent for one user query and return the final text answer."""
    result = build_travel_agent().invoke({"messages": [HumanMessage(content=query)]})
    return str(result["messages"][-1].content)
