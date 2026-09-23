import unittest

from langchain_core.messages import HumanMessage

from app.multi_agent import (
    FINISH,
    LANGUAGE_ADVISOR,
    TRAVEL_PLANNER,
    VISUALIZER,
    REPORTER,
    build_multi_agent,
)


def make_worker(name: str, content: str):
    def worker(state):
        return {
            "messages": [HumanMessage(content=content, name=name)],
            "completed": [name],
        }

    return worker


def route_in_order(state):
    for name in [TRAVEL_PLANNER, LANGUAGE_ADVISOR, VISUALIZER]:
        if name not in state["completed"]:
            return name
    return FINISH


def route_finish_early(state):
    return FINISH


def mock_reporter(state):
    return {"messages": [HumanMessage(content="/output/travel.pdf", name="reporter")], "pdf_path": "/output/travel.pdf"}


class MultiAgentGraphTests(unittest.TestCase):
    def test_supervisor_prevents_premature_finish(self) -> None:
        workers = {
            TRAVEL_PLANNER: make_worker(TRAVEL_PLANNER, "三日行程"),
            LANGUAGE_ADVISOR: make_worker(LANGUAGE_ADVISOR, "常用表达"),
            VISUALIZER: make_worker(VISUALIZER, "/images/shanghai.png"),
        }
        graph = build_multi_agent(router=route_finish_early, workers=workers, reporter=mock_reporter)

        result = graph.invoke(
            {"messages": [HumanMessage(content="规划上海三日游")], "completed": []}
        )

        self.assertEqual(result["completed"], [TRAVEL_PLANNER, LANGUAGE_ADVISOR, VISUALIZER])
        self.assertEqual(result["messages"][-1].name, REPORTER)

    def test_supervisor_routes_all_workers_before_finishing(self) -> None:
        workers = {
            TRAVEL_PLANNER: make_worker(TRAVEL_PLANNER, "三日行程"),
            LANGUAGE_ADVISOR: make_worker(LANGUAGE_ADVISOR, "常用表达"),
            VISUALIZER: make_worker(VISUALIZER, "/images/shanghai.png"),
        }
        graph = build_multi_agent(router=route_in_order, workers=workers, reporter=mock_reporter)

        result = graph.invoke(
            {"messages": [HumanMessage(content="规划上海三日游")], "completed": []}
        )

        self.assertEqual(result["completed"], [TRAVEL_PLANNER, LANGUAGE_ADVISOR, VISUALIZER])
        self.assertEqual(
            [message.name for message in result["messages"] if getattr(message, "name", None)],
            [TRAVEL_PLANNER, LANGUAGE_ADVISOR, VISUALIZER, REPORTER],
        )
        self.assertEqual(result["messages"][-2].content, "/images/shanghai.png")
        self.assertEqual(result["messages"][-1].content, "/output/travel.pdf")
        self.assertEqual(result["pdf_path"], "/output/travel.pdf")
