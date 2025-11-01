# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys 
import os
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
import aiohttp

#turn off all the crap that is spit out from the agent
import warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.ERROR)

sys.path.insert(1, 'bt_fraud_agent')
import dotenv
dotenv.load_dotenv()

from agent import root_agent

# Define constants for identifying the interaction context
APP_NAME = "bt_fraud_agent"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

async def create_runner():
    print("creating runner")
# Create the specific session where the conversation will happen
    async with aiohttp.ClientSession() as runner_session:
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        # --- Runner ---
        # Key Concept: Runner orchestrates the agent execution loop.
        runner = Runner(
            agent=root_agent, # The agent we want to run
            app_name=APP_NAME,   # Associates runs with our app
            session_service=session_service # Uses our session manager
        )
        runner_session.close()
        return runner

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print("calling agent")
  async with aiohttp.ClientSession() as agent_async_session:
    #print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." 

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async with aiohttp.ClientSession() as event_session:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            # You can uncomment the line below to see *all* events during execution
            #print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
            if event.is_final_response():
                print("found final response")
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                break # Stop processing events once the final response is found
            await event_session.close()
    await agent_async_session.close()
    return final_response_text

async def run_conversation(transaction_information):
    print("running conversation")
    async with aiohttp.ClientSession() as run_convo_session:
        runner = await create_runner()

        analysis = await call_agent_async(transaction_information,
                                runner=runner,
                                user_id=USER_ID,
                                session_id=SESSION_ID
        )
        await runner.close()
        await run_convo_session.close()
        return analysis 

def run_fraud_agent(transaction_information):
    result = asyncio.run(run_conversation(transaction_information))
    return result

#print(run_fraud_agent("What is the current time in Ridgewood, NJ"))
