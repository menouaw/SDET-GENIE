import os
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
load_dotenv()

# Initialize the agents
qa_agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=os.environ.get("GOOGLE_API_KEY")),
    markdown=True,
)

code_gen_agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=os.environ.get("GOOGLE_API_KEY")),
    markdown=True,
)
