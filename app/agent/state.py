# from typing import TypedDict

# from .schemas import ContentStrategy


# class ContentState(TypedDict, total=False):
#     topic: str
#     business_goal: str
#     target_audience: str

#     strategy: ContentStrategy

#     website_content: str
#     linkedin_content: str
#     instagram_content: str

#     review_result: str
#     approved: bool



from typing import TypedDict


class AgentState(TypedDict, total=False):
    messages: list[dict]
    answer: str
    iterations: int
