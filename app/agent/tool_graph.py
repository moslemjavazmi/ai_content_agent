
import json
from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.core.llm import llm, LLM_MODEL
from app.agent.state import AgentState
from app.agent.tools import get_business_info
from app.agent.tool_schemas import BUSINESS_INFO_TOOL


SYSTEM_PROMPT = """
You are a content strategy assistant for a company
that designs websites and AI agents.

Use available tools when you need accurate business
information. Never invent company facts.

Answer the user clearly and helpfully.
"""

AVAILABLE_TOOLS = {
    "get_business_info": get_business_info,
}


def call_model(state: AgentState) -> dict:
    """Ask the LLM what to do next."""

    messages = list(state.get("messages", []))
    iterations = state.get("iterations", 0) + 1

    response = llm.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=[BUSINESS_INFO_TOOL],
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # Convert the SDK message into a dictionary
    # that can be added to the next API request.
    messages.append(
        assistant_message.model_dump(exclude_none=True)
    )

    updates = {
        "messages": messages,
        "iterations": iterations,
    }

    # If the model has no more tools to call,
    # its message is the final answer.
    if not assistant_message.tool_calls:
        updates["answer"] = assistant_message.content or ""

    return updates


def execute_tools(state: AgentState) -> dict:
    """Validate and execute requested Python tools."""

    messages = list(state.get("messages", []))
    last_message = messages[-1]
    tool_calls = last_message.get("tool_calls", [])

    for tool_call in tool_calls:
        function_info = tool_call["function"]
        tool_name = function_info["name"]

        # Never execute a function just because the model
        # mentions its name. It must be allowlisted.
        if tool_name not in AVAILABLE_TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")

        arguments = json.loads(function_info["arguments"])

        # This particular tool accepts no arguments.
        if tool_name == "get_business_info" and arguments:
            raise ValueError(
                "get_business_info accepts no arguments"
            )

        tool_function = AVAILABLE_TOOLS[tool_name]
        result = tool_function(**arguments)

        # The tool result must reference the exact tool call.
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(
                result,
                ensure_ascii=False,
            ),
        })

    return {"messages": messages}


def route_after_model(
    state: AgentState,
) -> Literal["execute_tools", "__end__"]:
    """Choose whether to execute tools or finish."""

    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]

    if last_message.get("tool_calls"):
        return "execute_tools"

    return END


builder = StateGraph(AgentState)

builder.add_node("call_model", call_model)
builder.add_node("execute_tools", execute_tools)

builder.add_edge(START, "call_model")

builder.add_conditional_edges(
    "call_model",
    route_after_model,
    {
        "execute_tools": "execute_tools",
        END: END,
    },
)

builder.add_edge("execute_tools", "call_model")

content_agent = builder.compile()


def run_business_agent(user_request: str) -> str:
    """Public entry point used by FastAPI."""

    initial_state: AgentState = {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        "answer": "",
        "iterations": 0,
    }

    result = content_agent.invoke(
        initial_state,
        config={"recursion_limit": 20},
    )

    answer = result.get("answer", "")

    if not answer:
        raise RuntimeError(
            "The agent finished without a final answer."
        )

    return answer
