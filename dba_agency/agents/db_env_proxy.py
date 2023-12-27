from agency_swarm import Agent
from agency_swarm import BaseTool
from pydantic import Field
from db_pseudo_env import db_task_api

_name = "ToT_task"

_description = """
responsible for taking specific tasks and executing them in the database environment (including databases, monitoring systems, etc.), planning and executing specific actions.
"""

_instruction = """ #Instructions for Database Environment Agent

### Task: Call the function or tools to interact with database environment.
### IMPORTANT: If a tool is used, return the results of the tool's execution to the CEO agent as is, without any analysis or processing.

You are a highly specialized GPT focused on SQL database operations for professional database administrators and developers.
You understand specific intents recieved from other agents and generates appropriate database actions using commands, scripts, or third-party tools.
Your primary objective is to interact effectively with SQL databases, providing accurate and advanced technical solutions.
you focuses on returning precise results and analyzing them for technical users.
You maintains a professional and straightforward tone, prioritizing technical accuracy and practicality over personalization, ensuring that its responses are detailed, relevant, and valuable to database professionals.
"""


class InteractWithDataBaseEnv(BaseTool):
    """Use this tool to interact with database environment.
    This tool recieve the text of the specific action (eg, command, scripts or third-party tools), it then execute in the database environment, and it will finally return the result."""

    specific_task: str = Field(..., description="The specific task interacting with database environment.")


    # This code will be executed if the agent calls this tool
    def run(self):
      db_task_response = db_task_api.Assign_DB_Task(self.specific_task)
      return str(db_task_response)

_tools=[InteractWithDataBaseEnv]

_file_folder=None


def create_agent(*, 
                 description=_description, 
                 instuction=_instruction, 
                 tools=_tools, 
                 files_folder=_file_folder):
    return Agent(name=_name,
                     tools=tools,
                     description=description,
                     instructions=instuction,
                     files_folder=files_folder)
