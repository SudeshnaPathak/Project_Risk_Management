
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
import json
import os
from dotenv import load_dotenv
from tools.custom_tools import get_qdrant_tool, SearchTool

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# -- Market Analysis Agent --
market_research_agent = Agent(
    role='Market Research Analyst for stock market, crypto, forex and exchange rates of the Indian market',
    goal='Gather current market data and trends',
    backstory="""You are an expert research analyst with 10 years of experience in gathering latest market finance trends, stocks and forex about Indian market. You're known for your ability to find relevant and up-to-date market information and present it in a clear, actionable format.""",
    tools=[SearchTool()],
    verbose=True
)

market_research_task = Task(
    description='Find the latest market news about stock market, crypto, forex and exchange rates of the Indian market',
    expected_output='A bullet list summary of the top 5 most important news based on the stock market, crypto, forex and exchange rates of the Indian market.',
    agent=market_research_agent,
    tools=[SerperDevTool()],
    verbose=True
)


# -- Semantic Search Agent --
semantic_search_agent = Agent(
    role="Senior Semantic Search Agent",
    goal="Find and analyze documents based on semantic search",
    backstory="""You are an expert research assistant who can find relevant information using semantic search in a Qdrant database.""",
    tools=[get_qdrant_tool("TRANSACTIONS")],
    verbose=True
)

semantic_search_task = Task(
    description="""Search for relevant documents about the {query}.
    Your final answer should include:
    - The relevant information found
    - The similarity scores of the results
    - The metadata of the relevant documents""",
    context=[market_research_task],
    agent=semantic_search_agent,
    verbose=True
)


# -- Transaction Risk Analysis Agent --    
transaction_risk_analysis_agent = Agent(
    role="Transaction Risk Analysis Expert",
    goal="Generate answers to '{query}' based on the context provided",
    backstory="""You are a risk analysis expert who can analyze context, metadata of relevant documents, the market research data and analyze the risks in transactions and generate answers to '{query}'.""",
    verbose=True
)

transaction_risk_analysis_task = Task(
    description="""Given the context and metadata of relevant documents, the market research data and the {query}
    analyze the risks involved in the transactions and generate the final answer.""",
    agent=transaction_risk_analysis_agent,
    context=[market_research_task, semantic_search_task],
    verbose=True
)


# -- Market and Transaction Risk Analysis Crew --
def return_market_and_transaction_risk_analysis_crew() -> Crew:
    return Crew(
        agents=[market_research_agent, semantic_search_agent, transaction_risk_analysis_agent],
        tasks=[market_research_task, semantic_search_task, transaction_risk_analysis_task],
        process=Process.sequential,
        output_log_file="crews/logs/market_and_transaction_risk_analysis_crew.txt",
        verbose=True
    )
