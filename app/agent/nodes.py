from app.core.llm import llm, LLM_MODEL

from .schemas import ContentStrategy
from .state import ContentState


def generate_strategy(
    state: ContentState,
):
    prompt = f"""
        You are a senior content marketing strategist.

        Our business:
        A company that designs websites and builds AI agents.

        Topic:
        {state["topic"]}

        Business goal:
        {state["business_goal"]}

        Target audience:
        {state["target_audience"]}

        Create a content strategy for this topic.

        Think about:
        - the best content angle
        - the main message
        - the audience's pain point
        - the call to action
        - the appropriate tone
        - the appropriate content type
        """

    completion = llm.chat.completions.parse(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert B2B content strategist."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format=ContentStrategy,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise RuntimeError(
            f"Model refused the request: {message.refusal}"
        )

    strategy = message.parsed

    if strategy is None:
        raise RuntimeError(
            "Model did not return a structured strategy."
        )

    return {
        "strategy": strategy
    }
def generate_content(
    state: ContentState,
):
    strategy = state["strategy"]

    website_content = f"""
    # {state["topic"]}

    {strategy.main_message}

    ## The problem

    {strategy.pain_point}

    ## Our approach

    Our company helps businesses solve this problem
    through professional website development and AI agents.

    ## Next step

    {strategy.call_to_action}
    """

    linkedin_content = f"""
    {strategy.main_message}

    The problem:

    {strategy.pain_point}

    Our approach:

    We help businesses solve these problems
    with websites and AI agents.

    {strategy.call_to_action}

    #AI #AIAgents #WebDevelopment
    """

    instagram_content = f"""
    🚀 {state["topic"]}

    {strategy.main_message}

    💡 Problem:

    {strategy.pain_point}

    🤖 Our approach:

    Websites + AI Agents

    👉 {strategy.call_to_action}

    #AI #AIAgents #Technology
    """

    return {
        "website_content": website_content,
        "linkedin_content": linkedin_content,
        "instagram_content": instagram_content,
    }

def review_content(state: ContentState):
    website = state["website_content"]

    if len(website.strip()) > 20:
        return {
            "review_result": "approved",
            "approved": True,
        }

    return {
        "review_result": "rejected",
        "approved": False,
    }


def regenerate_content(state: ContentState):
    return {
        "website_content": (
            state["website_content"]
            + "\n\nImproved version."
        ),
        "review_result": "approved",
        "approved": True,
    }


def publish_content(state: ContentState):
    print("Publishing content...")

    print("\nWebsite:")
    print(state["website_content"])

    print("\nLinkedIn:")
    print(state["linkedin_content"])

    print("\nInstagram:")
    print(state["instagram_content"])

    return {}