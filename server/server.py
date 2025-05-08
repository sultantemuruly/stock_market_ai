import yfinance as yf
from mcp.server.fastmcp import FastMCP
from colorama import Fore

mcp = FastMCP("server")


@mcp.tool()
def stock_price(stock_ticker: str) -> str:
    """Get the historical closing prices for a given stock over the past month.

    Use this tool when a user asks for recent price data or performance of a stock.
    Provide the stock ticker symbol (e.g., "AAPL", "GOOG", "TSLA") as input.

    Args:
        stock_ticker (str): The stock ticker to look up.

    Returns:
        str: A formatted string containing the stock ticker and its daily closing prices from the last month.
    """
    dat = yf.Ticker(stock_ticker)
    historical_prices = dat.history(period="1mo")
    last_months_closes = historical_prices["Close"]
    print(Fore.GREEN + str(last_months_closes))
    return str(
        f"Stock price over the last month for {stock_ticker}: {last_months_closes}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
