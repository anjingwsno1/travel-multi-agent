import operator
from typing import Annotated, Callable, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from app.model import create_chat_model
from app.observability import get_logger
from tools import create_travel_pdf, generate_image, get_weather


TRAVEL_PLANNER = "travel_planner"
LANGUAGE_ADVISOR = "language_advisor"
VISUALIZER = "visualizer"
FINISH = "FINISH"
REPORTER = "reporter"
MEMBERS = [TRAVEL_PLANNER, LANGUAGE_ADVISOR, VISUALIZER]


class MultiAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    completed: Annotated[Sequence[str], operator.add]
    next: str
    pdf_path: str


class Route(BaseModel):
    next: Literal["travel_planner", "language_advisor", "visualizer", "FINISH"]


WORKER_PROMPTS = {
    TRAVEL_PLANNER: """你是旅行规划专家。根据用户需求给出清晰、按天安排的旅行计划。
如需天气信息，请调用 get_weather。只输出旅行计划，不要承担语言建议或图片生成。""",
    LANGUAGE_ADVISOR: """你是旅行语言与沟通顾问。根据用户目的地和行程，给出实用中文沟通建议、常用表达和礼仪提醒。
只输出语言建议，不要生成行程或图片。""",
    VISUALIZER: """你是旅行视觉设计师。根据已有行程生成一张合适的旅行配图。
必须调用 generate_image，并且最终只返回该工具生成的本地图片路径。""",
}


def create_worker_node(name: str, model, tools: list[BaseTool]):
    worker = create_react_agent(model, tools, state_modifier=WORKER_PROMPTS[name])

    def worker_node(state: MultiAgentState):
        logger = get_logger()
        logger.info("event=worker.start worker=%s", name)
        result = worker.invoke({"messages": state["messages"]})
        final_message = result["messages"][-1]
        logger.info("event=worker.success worker=%s", name)
        return {
            "messages": [HumanMessage(content=str(final_message.content), name=name)],
            "completed": [name],
        }

    return worker_node


def create_supervisor_router(model) -> Callable[[MultiAgentState], str]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """你是旅行团队监督者。团队成员包括：travel_planner、language_advisor、visualizer。
根据用户请求、对话历史与已完成成员，选择下一位尚未完成且最合适的成员。
必须依次完成全部三位成员后才能选择 FINISH。只负责路由，不回答用户问题。\n
已完成成员：{completed}""",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    router_chain = prompt | model.with_structured_output(Route)

    def route(state: MultiAgentState) -> str:
        decision = router_chain.invoke(
            {
                "messages": state["messages"],
                "completed": ", ".join(state["completed"]) or "无",
            }
        )
        return decision.next

    return route


def build_travel_markdown(messages: Sequence[BaseMessage]) -> str:
    contributions = {
        message.name: str(message.content)
        for message in messages
        if getattr(message, "name", None) in MEMBERS
    }
    visual_path = contributions.get(VISUALIZER, "")
    itinerary = contributions.get(TRAVEL_PLANNER, "暂未生成行程。")
    language_tips = contributions.get(LANGUAGE_ADVISOR, "暂未生成语言建议。")
    image_section = f"![旅行配图]({visual_path})\n\n" if visual_path else ""
    return (
        "# 旅行方案\n\n"
        f"{image_section}"
        "## 行程安排\n\n"
        f"{itinerary}\n\n"
        "## 语言与沟通建议\n\n"
        f"{language_tips}\n"
    )


def create_reporter_node(state: MultiAgentState):
    get_logger().info("event=reporter.start")
    markdown_text = build_travel_markdown(state["messages"])
    pdf_path = create_travel_pdf.invoke({"markdown_text": markdown_text})
    get_logger().info("event=reporter.success")
    return {
        "messages": [HumanMessage(content=pdf_path, name=REPORTER)],
        "pdf_path": pdf_path,
    }


def build_multi_agent(
    model=None,
    router=None,
    workers: dict[str, Callable] | None = None,
    reporter: Callable | None = None,
):
    """Build a supervisor-routed travel team workflow."""
    if workers is None or router is None:
        active_model = model or create_chat_model()
    else:
        active_model = model

    active_workers = workers or {
        TRAVEL_PLANNER: create_worker_node(TRAVEL_PLANNER, active_model, [get_weather]),
        LANGUAGE_ADVISOR: create_worker_node(LANGUAGE_ADVISOR, active_model, []),
        VISUALIZER: create_worker_node(VISUALIZER, active_model, [generate_image]),
    }
    active_router = router or create_supervisor_router(active_model)

    def route_next(state: MultiAgentState) -> str:
        pending_members = [name for name in MEMBERS if name not in state["completed"]]
        requested_next = active_router(state)
        if not pending_members:
            selected_next = FINISH
        elif requested_next in pending_members:
            selected_next = requested_next
        else:
            selected_next = pending_members[0]
        get_logger().info(
            "event=supervisor.route requested=%s selected=%s", requested_next, selected_next
        )
        return selected_next

    workflow = StateGraph(MultiAgentState)
    workflow.add_node("supervisor", lambda state: {"next": route_next(state)})
    for name, worker in active_workers.items():
        workflow.add_node(name, worker)
        workflow.add_edge(name, "supervisor")
    workflow.add_node(REPORTER, reporter or create_reporter_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {**{name: name for name in MEMBERS}, FINISH: REPORTER},
    )
    workflow.add_edge(REPORTER, END)
    return workflow.compile()


def run_multi_agent(query: str) -> str:
    """Run the complete travel team and combine each role's final contribution."""
    get_logger().info("event=workflow.start workflow=multi_agent")
    result = build_multi_agent().invoke(
        {"messages": [HumanMessage(content=query)], "completed": []}
    )
    get_logger().info("event=workflow.success workflow=multi_agent")
    return str(result["pdf_path"])
