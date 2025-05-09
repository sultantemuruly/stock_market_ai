import yfinance as yf
from mcp.server.fastmcp import FastMCP
from colorama import Fore

mcp = FastMCP("server")


@mcp.prompt()
def general_prompt_handler(prompt: str) -> str:
    """
    Prompt template for summarising stock price.

    This prompt is used when summarizing the recent stock price data.
    It takes in formatted historical stock price data and returns a human-readable summary.

    Returns:
        str: A summary of the stock's recent performance.
    """
    return f"""You are a helpful financial assistant designed to summarise stock data.
Using the information below, summarise the pertinent points relevant to stock price movement, recent trends, or volatility.
Respond in a concise and professional tone.

Prompt: {prompt}"""


@mcp.tool()
def balance_sheet(stock_ticker: str, periods: int = 1) -> str:
    """
    Retrieve the balance sheet for a given company.

    Use this tool when a user asks for financial details like assets, liabilities,
    or shareholder equity. You can optionally request multiple recent quarters.

    Args:
        stock_ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT", "GOOG").
        periods (int, optional): The number of most recent quarters to retrieve. Defaults to 1.

    Returns:
        str: A formatted string containing the balance sheet for the requested number of quarters.
    """
    dat = yf.Ticker(stock_ticker)
    balance = dat.balance_sheet.iloc[:, :periods]
    print(Fore.GREEN + str(balance))
    return f"Balance Sheet for {stock_ticker} (last {periods} period(s)):\n{balance}"


@mcp.tool()
def income_statement(stock_ticker: str, periods: int = 1) -> str:
    """
    Retrieve the income statement for a given company.

    Use this tool when a user wants to analyze a company's revenue, expenses, and profit
    across the last n quarters.

    Args:
        stock_ticker (str): The stock ticker symbol.
        periods (int, optional): Number of recent quarters to retrieve. Defaults to 1.

    Returns:
        str: A formatted string containing the income statement data.
    """
    dat = yf.Ticker(stock_ticker)
    income = dat.financials.iloc[:, :periods]
    print(Fore.GREEN + str(income))
    return f"Income Statement for {stock_ticker} (last {periods} period(s)):\n{income}"


@mcp.tool()
def cash_flow_statement(stock_ticker: str, periods: int = 1) -> str:
    """
    Retrieve the cash flow statement for a given company.

    Use this tool to analyze liquidity, cash from operations, and financial flexibility.
    You can specify the number of most recent quarters.

    Args:
        stock_ticker (str): The stock ticker symbol.
        periods (int, optional): Number of recent quarters to retrieve. Defaults to 1.

    Returns:
        str: A formatted string of the company's cash flow statement.
    """
    dat = yf.Ticker(stock_ticker)
    cashflow = dat.cashflow.iloc[:, :periods]
    print(Fore.GREEN + str(cashflow))
    return f"Cash Flow Statement for {stock_ticker} (last {periods} period(s)):\n{cashflow}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
