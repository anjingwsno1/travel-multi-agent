import unittest

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from app.travel_agent import build_travel_agent


@tool
def mock_weather(location: str) -> str:
    """Return deterministic weather data for workflow testing."""
    return f"{location}: 晴，25°C"


class ScriptedModel:
    def __init__(self, responses: list[AIMessage]) -> None:
        self.responses = responses
        self.bound_tools = None

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def invoke(self, messages):
        return self.responses.pop(0)


class TravelAgentGraphTests(unittest.TestCase):
    def test_calls_tool_then_returns_final_answer(self) -> None:
        model = ScriptedModel(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "mock_weather", "args": {"location": "上海"}, "id": "weather-1"}
                    ],
                ),
                AIMessage(content="上海当前晴朗，25°C，适合外出游览。"),
            ]
        )
        agent = build_travel_agent(model=model, tools=[mock_weather])

        result = agent.invoke({"messages": [HumanMessage(content="上海天气如何？")]})

        self.assertEqual(model.bound_tools, [mock_weather])
        self.assertEqual(result["messages"][-1].content, "上海当前晴朗，25°C，适合外出游览。")
        self.assertEqual(result["messages"][-2].content, "上海: 晴，25°C")

    def test_returns_direct_answer_when_no_tool_is_requested(self) -> None:
        model = ScriptedModel([AIMessage(content="上海是一座充满活力的城市。")])
        agent = build_travel_agent(model=model, tools=[mock_weather])

        result = agent.invoke({"messages": [HumanMessage(content="介绍上海")]})

        self.assertEqual(result["messages"][-1].content, "上海是一座充满活力的城市。")
        self.assertEqual(len(result["messages"]), 2)
