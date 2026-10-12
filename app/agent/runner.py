import json

from app.core.llm import llm, LLM_MODEL
from app.agent.tools import get_business_info
from app.agent.tool_schemas import BUSINESS_INFO_TOOL


AVAILABLE_TOOLS = {
    "get_business_info": get_business_info,
}


def run_business_agent(user_request: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a content strategy assistant for a "
                "company that designs websites and AI agents. "
                "Use available tools when you need accurate "
                "business information. Never invent company facts."
            ),
        },
        {
            "role": "user",
            "content": user_request,
        },
    ]

    for _ in range(5):
        response = llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=[BUSINESS_INFO_TOOL],
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Save the model's response, including tool calls.
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # If the model doesn't request a tool, we're done.
        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        # Execute each requested tool.
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            if tool_name not in AVAILABLE_TOOLS:
                raise ValueError(
                    f"Unknown tool: {tool_name}"
                )

            arguments = json.loads(
                tool_call.function.arguments
            )

            if tool_name == "get_business_info" and arguments:
                raise ValueError(
                    "get_business_info accepts no arguments"
                )

            tool_function = AVAILABLE_TOOLS[tool_name]
            result = tool_function(**arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

    raise RuntimeError(
        "Agent exceeded the maximum number of iterations."
    )