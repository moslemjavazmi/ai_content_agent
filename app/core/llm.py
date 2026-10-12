import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


llm = OpenAI(
    api_key=os.environ["NEW_API"],
    base_url=os.environ["LLM_BASE_URL"],
)


LLM_MODEL = os.environ["LLM_MODEL"]