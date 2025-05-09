import os
from mcp.server.fastmcp import FastMCP
from colorama import Fore
from textblob import TextBlob
from newsapi import NewsApiClient
from dotenv import load_dotenv
import yfinance as yf
import re
from collections import defaultdict

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(api_key=api_key)

mcp = FastMCP("news_server")


@mcp.prompt()
def general_prompt_handler(prompt: str) -> str:
    """
    Prompt template for analyzing news and sentiment.
    This prompt is used when analyzing news articles and sentiment data.
    It takes in news data and returns a human-readable analysis.

    Returns:
        str: An analysis of news sentiment and key information.
    """
    return f"""You are a helpful financial news analyst designed to interpret news sentiment and coverage.
Using the information below, summarize the key points, sentiment trends, and potential impact on the company or market.
Respond in a concise and professional tone.

Prompt: {prompt}"""


@mcp.tool()
def get_company_news(company_ticker: str, days: int = 7) -> str:
    """
    Retrieve recent news articles for a specific company.

    Args:
        company_ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").
        days (int, optional): How many days back to fetch news. Defaults to 7.

    Returns:
        str: A formatted string containing recent news headlines and brief analysis.
    """
    # Convert ticker to company name for better search results
    company_name = company_ticker
    try:
        company = yf.Ticker(company_ticker)
        company_name = company.info.get("shortName")
    except Exception:
        pass

    try:
        articles = newsapi.get_everything(
            q=company_name, language="en", sort_by="publishedAt", page_size=10
        )

        if articles["status"] != "ok":
            print(Fore.RED + f"Error: {articles.get('message', 'Unknown error')}")
            return f"Error retrieving news for {company_name}: {articles.get('message', 'Unknown error')}"

        article_list = articles.get("articles", [])

        if not article_list:
            return f"No recent news found for {company_name} in the past {days} days."

        # Limit to 10 most recent articles
        article_list = article_list[:10]

        # Format results
        news_summary = (
            f"Recent News for {company_name} ({company_ticker}) - Last {days} days:\n\n"
        )

        for i, article in enumerate(article_list, 1):
            # Calculate sentiment
            title = article.get("title", "No title")
            description = article.get("description", "No description")
            content = title + ". " + description
            sentiment = TextBlob(content).sentiment

            sentiment_label = "Neutral"
            if sentiment.polarity > 0.2:
                sentiment_label = "Positive"
            elif sentiment.polarity < -0.2:
                sentiment_label = "Negative"

            news_summary += f"{i}. {title}\n"
            news_summary += (
                f"   Source: {article.get('source', {}).get('name', 'Unknown')}\n"
            )
            news_summary += (
                f"   Date: {article.get('publishedAt', 'Unknown date')[:10]}\n"
            )
            news_summary += (
                f"   Sentiment: {sentiment_label} ({sentiment.polarity:.2f})\n"
            )
            news_summary += f"   URL: {article.get('url', 'No URL')}\n\n"

        print(
            Fore.GREEN
            + f"Retrieved {len(article_list)} news articles for {company_name}"
        )
        return news_summary

    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
        return f"Error retrieving news: {str(e)}"


@mcp.tool()
def get_sentiment_analysis(company_ticker: str, days: int = 30) -> str:
    """
    Analyze overall sentiment trends for a company based on recent news.

    Args:
        company_ticker (str): The stock ticker symbol.
        days (int, optional): How many days of news to analyze. Defaults to 30.

    Returns:
        str: A sentiment analysis summary with positive/negative ratio and trends.
    """
    # Convert ticker to company name for better search results
    company_name = company_ticker
    try:
        company = yf.Ticker(company_ticker)
        company_name = company.info.get("shortName")
    except Exception:
        pass

    try:
        articles = newsapi.get_everything(
            q=company_name,
            language="en",
            sort_by="publishedAt",
            page_size=100,  # Get more articles for better analysis
        )

        if articles["status"] != "ok":
            print(Fore.RED + f"Error: {articles.get('message', 'Unknown error')}")
            return f"Error analyzing sentiment for {company_name}: {articles.get('message', 'Unknown error')}"

        article_list = articles.get("articles", [])

        if not article_list:
            return f"No news found for {company_name} in the past {days} days to analyze sentiment."

        # Analyze all articles
        total_articles = len(article_list)
        sentiments = []

        for article in article_list:
            title = article.get("title", "")
            description = article.get("description", "")
            content = title + ". " + description
            analysis = TextBlob(content).sentiment
            sentiments.append(analysis.polarity)

        # Calculate metrics
        avg_sentiment = sum(sentiments) / len(sentiments)
        positive_count = sum(1 for s in sentiments if s > 0.2)
        negative_count = sum(1 for s in sentiments if s < -0.2)
        neutral_count = total_articles - positive_count - negative_count

        sentiment_status = "Neutral"
        if avg_sentiment > 0.2:
            sentiment_status = "Positive"
        elif avg_sentiment < -0.2:
            sentiment_status = "Negative"

        # Format results
        result = f"Sentiment Analysis for {company_name} ({company_ticker}) - Past {days} days:\n\n"
        result += (
            f"Overall Sentiment: {sentiment_status} (Score: {avg_sentiment:.2f})\n"
        )
        result += f"Total Articles Analyzed: {total_articles}\n"
        result += f"Positive Articles: {positive_count} ({positive_count/total_articles*100:.1f}%)\n"
        result += f"Neutral Articles: {neutral_count} ({neutral_count/total_articles*100:.1f}%)\n"
        result += f"Negative Articles: {negative_count} ({negative_count/total_articles*100:.1f}%)\n"

        # Get sentiment trend
        if len(article_list) >= 6:
            recent = sentiments[: len(sentiments) // 2]
            older = sentiments[len(sentiments) // 2 :]
            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            trend = ""
            if recent_avg > older_avg + 0.1:
                trend = "Sentiment is improving in recent coverage."
            elif recent_avg < older_avg - 0.1:
                trend = "Sentiment is declining in recent coverage."
            else:
                trend = "Sentiment has remained stable over the analyzed period."

            result += f"\nTrend Analysis: {trend}\n"

        print(
            Fore.GREEN
            + f"Completed sentiment analysis for {company_name}: {sentiment_status}"
        )
        return result

    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
        return f"Error analyzing sentiment: {str(e)}"


@mcp.tool()
def get_market_buzz(days: int = 3, limit: int = 5) -> str:
    """
    Get the most discussed companies in recent financial news using regex-based org detection.

    Args:
        days (int, optional): How many days back to analyze. Defaults to 3.
        limit (int, optional): Number of top companies to return. Defaults to 5.

    Returns:
        str: A list of the most discussed companies with their sentiment scores.
    """
    keywords = "stock market OR financial markets OR Wall Street OR NYSE OR NASDAQ"

    try:
        articles = newsapi.get_everything(
            q=keywords,
            language="en",
            sort_by="popularity",
            page_size=100,
        )

        if articles["status"] != "ok":
            print(Fore.RED + f"Error: {articles.get('message', 'Unknown error')}")
            return f"Error retrieving market buzz: {articles.get('message', 'Unknown error')}"

        article_list = articles.get("articles", [])
        if not article_list:
            return f"No market news found for the past {days} days."

        org_counts = defaultdict(int)
        org_sentiments = defaultdict(list)

        # Regex pattern: two or more capitalized words, possibly containing '&' or '-' (e.g., 'Bank of America', 'Johnson & Johnson')
        org_pattern = re.compile(r"\b([A-Z][a-zA-Z]*(?:\s+(?:&\s+)?[A-Z][a-zA-Z]*)+)\b")

        for article in article_list:
            title = article.get("title", "")
            description = article.get("description", "")
            content = f"{title} {description}"

            matches = org_pattern.findall(content)

            sentiment = TextBlob(content).sentiment.polarity

            for match in matches:
                org_name = match.strip()
                if len(org_name) > 2:
                    org_counts[org_name] += 1
                    org_sentiments[org_name].append(sentiment)

        if not org_counts:
            return "No significant company mentions found in recent market news."

        # Sort orgs by frequency
        sorted_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)
        top_orgs = sorted_orgs[:limit]

        result = f"Top Companies in Market News (Past {days} days):\n\n"

        for i, (org, count) in enumerate(top_orgs, 1):
            avg_sentiment = sum(org_sentiments[org]) / len(org_sentiments[org])
            sentiment_label = "Neutral"
            if avg_sentiment > 0.2:
                sentiment_label = "Positive"
            elif avg_sentiment < -0.2:
                sentiment_label = "Negative"

            result += f"{i}. {org}\n"
            result += f"   Mentions: {count}\n"
            result += (
                f"   Overall Sentiment: {sentiment_label} ({avg_sentiment:.2f})\n\n"
            )

        print(Fore.GREEN + f"Retrieved market buzz for {len(top_orgs)} companies")
        return result

    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
        return f"Error retrieving market buzz: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
