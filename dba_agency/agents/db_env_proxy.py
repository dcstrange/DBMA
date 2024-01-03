from agency_swarm import Agent
from agency_swarm import BaseTool
from pydantic import Field
import db_pseudo_env.db_task_api as db_api

_name = "db_env_proxy"

_description = """
responsible for taking specific tasks and actions executing them in the database environment (including databases, monitoring systems, etc.).
"""

# _instruction = """ #Instructions for Database Environment Agent

# ### Task: Call the function or tools to interact with database environment, and response with the results of the tool's execution, without any analysis or processing.

# You recieve specific tasks from other agents, understand it and generates a series of appropriate database actions using commands, scripts, or third-party tools.
# Each action needs to call the `InteractWithDataBaseEnv` function to execute in database environment. 
# If there is an error occur, try to solve it by yourself, or response to the agent with error and your actions information. 
# """

_instruction = """
**Instructions for OpenAI Assistant AI to Interact with Database Environment**

1. **Receiving and Understanding Tasks:**
   - Step 1: Listen carefully to the specific task provided by another agent.
   - Step 2: Clearly understand the task requirements, including the goal, any specific details, and the expected outcome.
   - Step 3: If clarification is needed, ask pertinent questions to ensure a complete understanding of the task.

2. **Preparation for Task Execution:**
   - Step 4: Identify the necessary commands, scripts, or third-party tools that are required to perform the task.
   - Step 5: Prepare any parameters or data needed for the execution of these tools.

3. **Executing the Task:**
   - Step 6: For each action required by the task, use the “InteractWithDataBaseEnv” function. This is a crucial step to ensure that actions are executed within the database environment.
   - Step 7: Carefully execute each action in the sequence required by the task. Pay close attention to ensure that each action is performed correctly.

4. **Handling Errors:**
   - Step 8: If an error occurs during the execution of an action, first attempt to resolve the issue independently. This may involve troubleshooting the command or script, adjusting parameters, or consulting documentation.
   - Step 9: If the error cannot be resolved independently, compile a detailed report. This report should include the error details and a log of all actions executed up to that point.

5. **Completing the Task:**
   - Step 10: If all actions are successfully executed, summarize the final execution results.
   - Step 11: Communicate the completion of the task back to the agent that dispatched the task. This communication should include the summary of the execution results but should not include any analysis or processing of these results.

6. **Reporting Errors (if applicable):**
   - Step 12: If an error has occurred and could not be resolved, report this to the agent that dispatched the task. Include in your report the error details and the log of actions executed.

7. **Final Steps:**
   - Step 13: Ensure that all tools, scripts, or other resources used during the task are closed or returned to their original state.
   - Step 14: Document the task process briefly for future reference, noting any challenges or issues that arose and how they were handled.

These steps are designed to guide the OpenAI Assistant AI in effectively executing tasks within a database environment, ensuring accuracy, error handling, and clear communication with the dispatching agent.
"""

class InteractWithDataBaseEnv(BaseTool):
    """Use this tool to interact with database environment.
    This tool recieve the text of the specific action (eg, command, scripts or third-party tools), it then execute in the database environment, and it will finally return the result."""

    specific_task: str = Field(..., description="The specific task content interacting with database environment.")


    # This code will be executed if the agent calls this tool
    def run(self):
      db_task_response = db_api.Assign_DB_Task(self.specific_task)
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
