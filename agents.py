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
from autogen_agentchat.agents import AssistantAgent

# Import tools for each agent and parse them
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

# Define Document Agent
document_agent = AssistantAgent(
    name="Document_Agent",
    description=config["agents"]["DocumentAgent"]["description"],
    tools=[parse_document],
    model_client=watsonx_client,
    system_message=config["agents"]["DocumentAgent"]["system_message"],
    reflect_on_tool_use=True
)

# Define SQL Agent
sql_agent = AssistantAgent(
    name="SQL_Agent",
    description=config["agents"]["SQLAgent"]["description"],
    tools=[sql_query_tool],
    model_client=watsonx_client,
    system_message=config["agents"]["SQLAgent"]["system_message"],
    reflect_on_tool_use=True
)

# Utility function to retrieve all agents as a list
def get_all_agents():
    return [document_agent, sql_agent]
