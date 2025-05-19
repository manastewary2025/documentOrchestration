import os
import json
from dotenv import load_dotenv

# Load the JSON configuration
with open("config.json", "r") as f:
    config = json.load(f)

# Load environment variables
load_dotenv()

# Import WatsonX client
from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent

# Import tools for each agent
from tools.document_parser import parse_document  # your custom document parsing logic
from tools.sql_tool import sql_query_tool         # your custom SQL-to-query logic

# Custom WatsonX client (with a no-op close method)
class CustomWatsonXChatCompletionClient(WatsonXChatCompletionClient):
    def close(self):
        pass

# Instantiate WatsonX model client
watsonx_client = CustomWatsonXChatCompletionClient(
    model_id="ibm/granite-3-2-8b-instruct",
    api_key=os.environ.get("WATSONX_API_KEY"),
    url=os.environ.get("WATSONX_URL"),
    project_id=os.environ.get("WATSONX_PROJECT_ID")
)


def get_all_agents():
    user_proxy = UserProxyAgent(name="User_Proxy")

    document_agent = AssistantAgent(
        name="Document_Agent",
        model_client=watsonx_client,  # use the instantiated model client
        tools=[parse_document],
        description="Extracts structured info from documents",
    )


    sql_agent = AssistantAgent(
        name="SQL_Agent",
        model_client=watsonx_client,  # <-- Correct field
        description="Generates SQL queries based on parsed document content.",
        tools=[sql_query_tool]
    )


    return {
        "User_Proxy": user_proxy,
        "Document_Agent": document_agent,
        "SQL_Agent": sql_agent,
    }
    
