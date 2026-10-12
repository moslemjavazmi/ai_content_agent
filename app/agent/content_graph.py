
import json
from typing import Literal

from pydantic import ValidationError
from langgraph.graph import StateGraph, START, END

from app.core.llm import llm, LLM_MODEL
from app.agent.tools import get_business_info
from app.agent.schemas import ContentDraft
from app.agent.content_state import ContentAgentState
from app.services.image_service import (
    generate_image as request_image_generation,
    ImageServiceError,
)

def load_business_context(
    state: ContentAgentState,
) -> dict:
    """Load the trusted business information."""

    return {
        "business_context": get_business_info(),
    }


def generate_content(
    state: ContentAgentState,
) -> dict:
    """Generate a structured social media content draft."""

    context = state["business_context"]
    topic = state["topic"]
    platform = state["platform"]
    attempts = state.get("attempts", 0) + 1
    previous_errors = state.get("validation_errors", [])

    repair_instructions = ""

    if previous_errors:
        repair_instructions = (
            "\nThe previous output failed validation.\n"
            "Fix these problems:\n"
            + "\n".join(previous_errors)
        )

    system_prompt = """
You are a professional social media content strategist.

Create useful, honest, audience-focused content.
Use only the business facts provided in the context.
Do not invent clients, testimonials, statistics,
guarantees, or company achievements.

Return exactly one valid JSON object.
Do not wrap it in Markdown or code fences.

The JSON must contain these fields:
platform, topic, content_angle, main_message,
post_text, caption, call_to_action, hashtags,
visual_prompt.

platform must be either "instagram" or "linkedin".
hashtags must be a JSON array of strings.
All other fields must be strings.
"""

    user_prompt = f"""
Business information:
{json.dumps(context, ensure_ascii=False)}

Requested platform: {platform}
Requested topic: {topic}

Create a suitable post for this platform and topic.
Write all user-facing content in Persian.
The visual_prompt should describe an image suitable
for the post, without asking the image model to
render text inside the image.

{repair_instructions}
"""

    response = llm.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    raw_content = response.choices[0].message.content

    if not raw_content:
        raw_content = ""

    return {
        "raw_content": raw_content,
        "attempts": attempts,
        "is_valid": False,
        "content": {},
    }


def validate_content(
    state: ContentAgentState,
) -> dict:
    """Parse JSON and validate it with Pydantic."""

    try:
        draft = ContentDraft.model_validate_json(
            state.get("raw_content", "")
        )

        # Ensure the output matches the requested platform.
        if draft.platform != state["platform"]:
            raise ValueError(
                "platform must match the requested platform"
            )

        return {
            "content": draft.model_dump(),
            "validation_errors": [],
            "is_valid": True,
        }

    except (ValidationError, ValueError) as exc:
        if isinstance(exc, ValidationError):
            errors = [
                (
                    f"{'.'.join(str(part) for part in item['loc'])}: "
                    f"{item['msg']}"
                )
                for item in exc.errors()
            ]
        else:
            errors = [str(exc)]

        return {
            "content": {},
            "validation_errors": errors,
            "is_valid": False,
        }



def route_after_validation(
    state: ContentAgentState,
) -> Literal["build_image_prompt", "retry", "done"]:

    if state.get("is_valid", False):
        return "build_image_prompt"

    if state.get("attempts", 0) < 3:
        return "retry"

    return "done"

def create_content(
    topic: str,
    platform: Literal["instagram", "linkedin"],
) -> dict:
    """Run the graph and return a validated content draft."""

    result = content_graph.invoke(
        {
            "topic": topic,
            "platform": platform,
            "attempts": 0,
            "validation_errors": [],
            "is_valid": False,
        },
        config={"recursion_limit": 15},
    )

    if not result.get("is_valid"):
        errors = result.get("validation_errors", [])
        raise RuntimeError(
            "Content generation failed validation: "
            + "; ".join(errors)
        )

    return result["content"]



def build_image_prompt(
    state: ContentAgentState,
) -> dict:
    """Prepare a visual prompt for the image provider."""

    content = state["content"]

    prompt = f"""
Create a professional social media visual.

Topic: {content["topic"]}
Main message: {content["main_message"]}
Visual direction: {content["visual_prompt"]}

Style:
- Modern and professional
- Suitable for a web design and AI automation company
- Clean composition with a clear visual focal point
- No watermarks
- Do not render text, logos, or fake UI text inside the image
"""

    return {"image_prompt": prompt.strip()}


def generate_image_node(
    state: ContentAgentState,
) -> dict:
    """Generate an image or report why it was unavailable."""

    try:
        result = request_image_generation(
            state["image_prompt"]
        )
        result["url_path"] = (
            f"/media/generated/{result['filename']}"
        )
        return {
            "image_result": result,
            "image_error": "",
        }

    except ImageServiceError as exc:
        # Keep the text package usable even when image
        # generation has not been configured or fails.
        return {
            "image_result": {
                "status": "not_generated",
            },
            "image_error": str(exc),
        }


def assemble_content_package(
    state: ContentAgentState,
) -> dict:
    """Combine validated text and image metadata."""

    return {
        "package": {
            "content": state["content"],
            "image_prompt": state["image_prompt"],
            "image": state.get(
                "image_result",
                {"status": "not_generated"},
            ),
            "image_error": state.get("image_error", ""),
        }
    }





builder = StateGraph(ContentAgentState)

builder.add_node(
    "load_business_context",
    load_business_context,
)
builder.add_node("generate_content", generate_content)
builder.add_node("validate_content", validate_content)
builder.add_node("build_image_prompt", build_image_prompt)
builder.add_node("generate_image", generate_image_node)
builder.add_node(
    "assemble_content_package",
    assemble_content_package,
)

builder.add_edge(START, "load_business_context")
builder.add_edge(
    "load_business_context",
    "generate_content",
)
builder.add_edge("generate_content", "validate_content")

builder.add_conditional_edges(
    "validate_content",
    route_after_validation,
    {
        "retry": "generate_content",
        "build_image_prompt": "build_image_prompt",
        "done": END,
    },
)

builder.add_edge("build_image_prompt", "generate_image")
builder.add_edge("generate_image", "assemble_content_package")
builder.add_edge("assemble_content_package", END)

content_graph = builder.compile()

