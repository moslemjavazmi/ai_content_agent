
from typing import TypedDict, Any


class ContentAgentState(TypedDict, total=False):
    topic: str
    platform: str
    business_context: dict[str, Any]

    raw_content: str
    content: dict[str, Any]

    validation_errors: list[str]
    is_valid: bool
    attempts: int

    
    image_prompt: str
    image_result: dict
    image_error: str
    package: dict

