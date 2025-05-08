from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = LiteLLMModel(
    model_id="gpt-4o",
    api_key=api_key,
)

server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "../server/server.py"],
    env=None,
)

with ToolCollection.from_mcp(
    server_parameters, trust_remote_code=True
) as tool_collection:
    agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
    agent.run("What you can tell about Apple's cash flow statement in last quarter?")
