from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
#from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
#from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
import asyncio
import os

from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

load_dotenv()

# Custom WatsonX client (with a no-op close method)
class CustomWatsonXChatCompletionClient(WatsonXChatCompletionClient):
    def close(self):
        """Implement the required close method"""
        pass  # Add cleanup logic if needed

# Instantiate the WatsonX model client
az_model_client = CustomWatsonXChatCompletionClient(
    model_id="ibm/granite-3-2-8b-instruct",  # WORKING
    api_key=os.environ.get("WATSONX_API_KEY"),
    url=os.environ.get("WATSONX_URL"),
    project_id=os.environ.get("WATSONX_PROJECT_ID")
)

# Planner Agent
PlannerAgent = AssistantAgent(
    "PlannerAgent",
    description="Coordinates between Document and SQL agents to extract and validate insights.",
    model_client=az_model_client,
    system_message="""
    You are the PlannerAgent.
    Your job is to break down the task into:
        1. Extract insights from the document using DocumentAgent
        2. Use SQLAgent to verify or enrich the insights from a database

    Team Members:
      - DocumentAgent: extracts, summarizes, and highlights key insights from text.
      - SQLAgent: queries the SQL database to verify data points or fetch related values.

    Assign tasks using this format:
    1. <agent> : <task>

    After all subtasks are done, summarize the results and respond with 'TERMINATE'.
    """
)

# Document Agent
DocumentAgent = AssistantAgent(
    "DocumentAgent",
    model_client=az_model_client,
    system_message="""
    You are a document processing expert.

    Instead of waiting for real input, always return this static analysis:

    "Document Analysis Result:
    - Product: Widget A
    - Sales Figure: $120,000
    - Region: North America
    - Time Period: Q1 2024"

    Respond to any task with the above output as if you had already analyzed the document.
    """
)


# SQL Agent
SQLAgent = AssistantAgent(
    "SQLAgent",
    model_client=az_model_client,
    system_message="""
    You are a SQL expert.

    Always respond with the following static verification output:

    "SQL Verification Result:
    - Verified Product: Widget A
    - Database Sales Figure: $118,500
    - Discrepancy: -$1,500
    - Comment: Document figure is slightly higher than database record. May include returns or forecasted data."

    You do not need real database access. Assume this result is accurate and return it when asked to verify sales data.
    """
)


# Termination logic
termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=10)

# Group Chat
team = SelectorGroupChat(
    [PlannerAgent, DocumentAgent, SQLAgent],
    model_client=az_model_client,
    termination_condition=termination,
)

# Main entry point
async def main():
    await Console(
        team.run_stream(
            #task="Analyze the provided document and verify if the mentioned sales figures match the database."
            #task="Compare the Q1 2024 sales data from the uploaded sales report document with the database and highlight discrepancies."
            #task="Analyze the customer complaint document and verify if the issues raised match the ticket resolution logs in the database."
            
        )
    )

if __name__ == "__main__":
    asyncio.run(main())
