import os
import asyncio
import json

from dotenv import load_dotenv
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

# Load the JSON configuration
with open("config.json", "r") as f:
    config = json.load(f)

# Load environment variables
load_dotenv()

# Import agents and watsonx client
from agents import get_all_agents, watsonx_client

# Termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=6)
termination = text_mention_termination | max_messages_termination

# Selector prompt for agent routing
selector_prompt = config["selector_prompt"]

# Create the agent team
agents = get_all_agents()
team = SelectorGroupChat(
    agents,  # passed positionally
    model_client=watsonx_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,
)


# Task: document query
if __name__ == "__main__":
    task = "Extract property and developer details from the uploaded PDF and generate a SQL query to fetch their transaction history."

    async def main():
        final_response = None
        async for response in team.run_stream(task=task):
            final_response = response

        if final_response and final_response.messages:
            final_message = final_response.messages[-1]
            print("\n ########## Final Response ##########\n")
            print("Agent:", final_message.source)
            print("Content:\n", final_message.content)
        else:
            print("No messages found.")

    asyncio.run(main())
