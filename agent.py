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

system_prompt = """
You are a specialized financial assistant focused exclusively on providing information and analysis related to finance, stocks, and companies. Use the available tools (e.g., income_statement, balance_sheet, get_sentiment_analysis) to answer queries about financial data, stock performance, or company news. Provide concise and professional responses.

If the user asks about topics unrelated to finance or companies (e.g., weather, general knowledge, personal advice), politely respond: "I'm a finance agent and can only assist with financial or company-related questions. Please ask about stocks, financial data, or company news."

For stock-related queries (e.g., buy/hold/sell decisions), use relevant financial data (e.g., income statement, balance sheet) and news sentiment to provide a clear recommendation. Avoid redundant tool calls and prioritize efficiency.
"""

financial_server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "--no-project", "./servers/financial_data_server.py"],
    env=None,
)

news_server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "--no-project", "./servers/news_server.py"],
    env=None,
)

# Connect to both servers and combine tools
with (
    ToolCollection.from_mcp(
        financial_server_parameters, trust_remote_code=True
    ) as financial_tools,
    ToolCollection.from_mcp(
        news_server_parameters, trust_remote_code=True
    ) as news_tools,
):
    combined_tools = [*financial_tools.tools, *news_tools.tools]
    agent = ToolCallingAgent(
        tools=combined_tools, model=model, system_prompt=system_prompt
    )

    agent.run("Should I buy, hold, or sell Apple stocks?")
