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
import dotenv
dotenv.load_dotenv()

#basic agent imports (some used in agent_analyzer)
from google.adk.agents.llm_agent import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.planners import BasePlanner, BuiltInPlanner, PlanReActPlanner
from google.adk.models import LlmRequest

#Bigtable tools 
from google.adk.tools.google_tool import GoogleTool
from google.adk.tools.bigtable import query_tool
from google.adk.tools.bigtable.settings import BigtableToolSettings
from google.adk.tools.bigtable.bigtable_credentials import BigtableCredentialsConfig
from google.adk.tools.bigtable.bigtable_toolset import BigtableToolset
from google.adk.tools.tool_context import ToolContext
import google.auth
from google.auth.credentials import Credentials

#load my prompt from seperate file
sys.path.insert(1, 'bt_fraud_agent')
import prompt

sys.path.insert(1, 'bt_utils')
import btconfig

tool_settings = BigtableToolSettings()

# Define a credentials config - in this example we are using application default
# credentials
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = BigtableCredentialsConfig(
    credentials=application_default_credentials
)

# Instantiate a Bigtable toolset
bigtable_toolset = BigtableToolset(
    credentials_config=credentials_config, bigtable_tool_settings=tool_settings
)

def find_bigtable_transactions(
    credit_card_number: int,
    credentials: Credentials,  # GoogleTool handles `credentials`
    settings: BigtableToolSettings,  # GoogleTool handles `settings`
    tool_context: ToolContext,  # GoogleTool handles `tool_context`
):
  """Use this tool to get a list of recent transactions for a credit care number from Bigtable.

  Returns:
      A list of transactions from Bigtable for a specific credit card to be used in a fraud analysis.
  """

  # Replace the following settings for a specific bigtable database.
  #PROJECT_ID = "google.com:cloud-bigtable-dev"
  PROJECT_ID = btconfig.get_project_id()
  INSTANCE_ID = btconfig.get_instance_id()

  query = f"""
   SELECT * FROM v_transactions where credit_card_number = {credit_card_number}
    """

  return query_tool.execute_sql(
      project_id=PROJECT_ID,
      instance_id=INSTANCE_ID,
      query=query,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
  )


# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

def say_hi():
    return "hi"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Run a fraud analysis based on data in Bigtable.",
    instruction=prompt.BIGTABLE_FRAUD_PROMPT,
    tools=[
        bigtable_toolset,
        GoogleTool(
            func=find_bigtable_transactions,
            credentials_config=credentials_config,
            tool_settings=tool_settings,
        )
    ],
)

