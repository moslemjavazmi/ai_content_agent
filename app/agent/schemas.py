

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

class ContentStrategy(BaseModel):
    content_angle: str = Field(
        description="The main angle of the content."
    )

    main_message: str = Field(
        description="The main message the audience should remember."
    )

    pain_point: str = Field(
        description="The main problem or pain point of the target audience."
    )

    call_to_action: str = Field(
        description="The desired action from the audience."
    )

    tone: str = Field(
        description="The tone of the content."
    )

    content_type: str = Field(
        description="The type of content, such as educational, promotional, or case study."
    )




class ContentDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal["instagram", "linkedin"]

    topic: str = Field(min_length=3, max_length=200)

    content_angle: str = Field(min_length=5, max_length=300)

    main_message: str = Field(min_length=10, max_length=500)

    post_text: str = Field(min_length=20, max_length=3000)

    caption: str = Field(min_length=10, max_length=2200)

    call_to_action: str = Field(min_length=3, max_length=200)

    hashtags: list[str] = Field(
        min_length=1,
        max_length=15,
    )

    visual_prompt: str = Field(
        min_length=10,
        max_length=1000,
    )
