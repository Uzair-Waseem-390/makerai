import os 
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

gemini_clint = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)

gemini_model1 = OpenAIChatCompletionsModel(openai_client=gemini_clint, model="gemini-2.5-flash")

gemini_model2 = OpenAIChatCompletionsModel(openai_client=gemini_clint, model="gemini-2.5-flash-lite")