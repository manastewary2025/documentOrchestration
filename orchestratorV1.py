import os
import asyncio
import json

from dotenv import load_dotenv
#from autogen_agentchat.teams import GroupChat, GroupChatManager
from autogen import GroupChat, GroupChatManager,AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

from agentsV1 import get_all_agents, watsonx_client

# Load environment
load_dotenv()

# Load the JSON configuration
with open("config.json", "r") as f:
    config = json.load(f)

# Termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=8)
termination = text_mention_termination | max_messages_termination

# Get agents
agents = get_all_agents()
agent_list = [agent for name, agent in agents.items()]
user_proxy = agents["User_Proxy"]

# Define group chat (multi-agent)
groupchat = GroupChat(
    agents=agent_list,
    messages=[],
    max_round=8,
    speaker_transitions_type="manual",
    allowed_speaker_transitions={
        user_proxy: [agents["Document_Agent"], agents["SQL_Agent"]],
        agents["Document_Agent"]: [agents["SQL_Agent"]],
        agents["SQL_Agent"]: [user_proxy],
    },
)


# Manager to orchestrate
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=watsonx_client,
    human_input_mode="NEVER",
    enable_termination=True,
    termination_condition=termination,
)

# Task: document + SQL
if __name__ == "__main__":
    task = "Extract developer and project information from the PDF and generate an SQL query to retrieve their transaction history."

    async def main():
        final_response = None
        async for response in manager.run_stream(task=task, sender=user_proxy):
            final_response = response

        if final_response and final_response.messages:
            final_message = final_response.messages[-1]
            print("\n ########## Final Response ##########\n")
            print("Agent:", final_message.source)
            print("Content:\n", final_message.content)
        else:
            print("No messages found.")

    asyncio.run(main())
