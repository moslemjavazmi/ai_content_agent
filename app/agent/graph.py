from typing import Literal

from langgraph.graph import StateGraph, START, END

from .state import ContentState
from .nodes import (
    generate_strategy,
    generate_content,
    review_content,
    regenerate_content,
    publish_content,
)


def review_router(
    state: ContentState,
) -> Literal["publish", "regenerate"]:
    if state["approved"]:
        return "publish"

    return "regenerate"


builder = StateGraph(ContentState)


builder.add_node(
    "strategy",
    generate_strategy,
)

builder.add_node(
    "generate_content",
    generate_content,
)

builder.add_node(
    "review",
    review_content,
)

builder.add_node(
    "regenerate",
    regenerate_content,
)

builder.add_node(
    "publish",
    publish_content,
)


builder.add_edge(
    START,
    "strategy",
)

builder.add_edge(
    "strategy",
    "generate_content",
)

builder.add_edge(
    "generate_content",
    "review",
)


builder.add_conditional_edges(
    "review",
    review_router,
    {
        "publish": "publish",
        "regenerate": "regenerate",
    },
)


builder.add_edge(
    "regenerate",
    "review",
)

builder.add_edge(
    "publish",
    END,
)


content_agent = builder.compile()