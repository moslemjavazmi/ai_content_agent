from app.core.llm import llm, LLM_MODEL
from app.agent.schemas import ContentStrategy


completion = llm.chat.completions.parse(
    model=LLM_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a professional B2B marketing strategist.",
        },
        {
            "role": "user",
            "content": """
Create a content strategy for:

Topic:
Why businesses should use AI agents

Business goal:
Generate leads

Target audience:
Small and medium-sized businesses
""",
        },
    ],
    response_format=ContentStrategy,
)


message = completion.choices[0].message
print(message)

if message.refusal:
    print("REFUSED:")
    print(message.refusal)
else:
    strategy = message.parsed

    print("CONTENT ANGLE:")
    print(strategy.content_angle)

    print("\nMAIN MESSAGE:")
    print(strategy.main_message)

    print("\nPAIN POINT:")
    print(strategy.pain_point)

    print("\nCALL TO ACTION:")
    print(strategy.call_to_action)

    print("\nTONE:")
    print(strategy.tone)

    print("\nCONTENT TYPE:")
    print(strategy.content_type)