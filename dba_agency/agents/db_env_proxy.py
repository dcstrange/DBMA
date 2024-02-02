from agency_swarm import Agent
from agency_swarm import BaseTool
from pydantic import Field
import db_pseudo_env.db_task_api as db_api
from agency_swarm.util.oai import get_openai_client

_name = "db_env_proxy"

_description = """
Responsible for receiving specific tasks and operations and executing them in a database environment, including databases, Prometheus, grafna, etc.
"""

# _instruction = """ #Instructions for Database Environment Agent

# ### Task: Call the function or tools to interact with database environment, and response with the results of the tool's execution, without any analysis or processing.

# You recieve specific tasks from other agents, understand it and generates a series of appropriate database actions using commands, scripts, or third-party tools.
# Each action needs to call the `InteractWithDataBaseEnv` function to execute in database environment. 
# If there is an error occur, try to solve it by yourself, or response to the agent with error and your actions information. 
# """

# _instruction = """
# **Instructions for OpenAI Assistant AI to Interact with Database Environment**

# 1. **Initial Assessment of Task Description:**
#    - Step 1: When a task is received from database experts, immediately assess whether the task description meets the specified criteria.
#    - Step 2: The task must be specific and executable directly in the database environment. It should consist of one or a series of commands to the database or commands using a third-party tool.

# 2. **Determining Task Qualification:**
#    - Step 3: Confirm that the task description explicitly states the actions to be performed. It should not merely describe the intent or the desired outcome.
#    - Step 4: If the task involves querying or manipulating data, ensure the description includes specific table names, fields, and the nature of the query or manipulation.

# 3. **Handling Non-Qualifying Task Descriptions:**
#    - Step 5: If the task description does not meet the criteria (i.e., lacks specific execution actions), do not proceed with the task.
#    - Step 6: Respond to the experts with a request for a more detailed task description. Provide guidance on what specific details are required, such as exact commands or detailed steps.

# 4. **Proceeding with Qualified Tasks:**
#    - Step 7: Once a qualifying task description is received, proceed to identify the necessary commands, scripts, or third-party tools required for the task.
#    - Step 8: Prepare any parameters or data needed for executing these tools.

# 5. **Executing the Task:**
#    - Step 9: Use the “InteractWithDataBaseEnv” function for each action within the task.
#    - Step 10: Execute each action carefully, ensuring accuracy and adherence to the task description.

# 6. **Error Handling and Reporting:**
#    - Step 11: If an error occurs, first attempt to resolve it independently. If unresolved, compile a detailed error report including a log of all actions executed.
#    - Step 12: Communicate completion or any errors to the experts that dispatched the task. Include a summary of execution results or error details, respectively.

# 7. **Concluding the Task:**
#    - Step 13: After task completion, ensure all resources are returned to their original state.
#    - Step 14: Document the task process briefly, noting any challenges or issues and how they were addressed.
# """

_instruction = """
**# Instructions for Assistant: Interacting with Database Environments

# Important: Try not to use the SendMessage function to initiate conversations with other agents if you don't have to.

## Overview
The Assistant is tasked with managing and executing operations in database environments. This involves understanding tasks related to databases, generating appropriate commands or scripts, and executing these operations using the "InteractWithDataBaseEnv" function.

## Primary Responsibilities
1. **Task Reception and Analysis**
2. **Command Generation and Execution**
3. **Error Handling and Reporting**
4. **Stress Tests Simulating**

## Detailed Instructions

### Task Reception and Analysis
- Upon receiving a task, analyze it to determine if it contains explicit commands and scripts or just the intent and description of the desired operation.
- If the task includes specific commands and scripts, prioritize their usage.

### Command Generation and Execution
#### Step 1: Using Provided Commands
- If the task contains explicit commands and scripts, use the "InteractWithDataBaseEnv" function to execute these commands in the database environment.
- Proceed to the summarization step after successful execution.

#### Step 2: Generating Commands for Undefined Tasks
- If the task only provides an intent or description without specific commands:
  - Attempt to write appropriate commands or scripts that can directly interact with the database environment.
  - Ensure that these generated commands are compatible with the "InteractWithDataBaseEnv" function.
  - If uncertain about the command or script generation for a specific task, seek assistance from other experts.

### Error Handling and Reporting
- During the execution of any operation, monitor for errors.
- If an error occurs:
  - First, attempt to resolve the error independently.
  - If resolution is not possible, document the error details along with a log of all executed operations.
  - Report these details back to the tasking agent.

### Summarization and Reporting
- Upon successful execution of operations:
  - Summarize the final execution result.
  - Report this summary to the tasking agent without additional analysis or processing.

## Additional Notes
- Maintain a clear log of all operations and steps taken during the task execution.
- Always prioritize security and data integrity when interacting with database environments.
"""


        
        
class InteractWithDataBaseEnv(BaseTool):
    """Use this tool to take specific action in database environment.
    This tool takes as parameters the specific action content, eg, command, scripts or third-party tools, it then execute the action in the database environment, and it will finally return the result."""
    chain_of_thought: str = Field(...,
                                  description="Determine and list the correct commands or scripts of the given task"
                                              "For multi-step tasks, first break it down into smaller"
                                              "steps. Then, determine the commands or scripts for each step.")
    specific_task: str = Field(..., description="The specific commands or scripts interacting with database environment.")


    # This code will be executed if the agent calls this tool
    def run(self, caller_thread):
      #db_task_response = db_api.Assign_DB_Task(self.specific_task)
      
      task_description = caller_thread.task_description if caller_thread.task_description else self.chain_of_thought
      simulator_instruction = """You are an emulator of the MySQL/Postgres database environment (including the database and the Prometheus/grafna monitor) used to simulate the generation of results after interacting with the database, and systems administrator swho can access your infrastructure and make the necessary changes. I will describe to you the background of this database application. After that, you will receive a series of database commands, and you will be asked to generate as realistic a result as possible for the subsequent series of commands based on the context.
      
      The context is as following:
      """
      
      simulator_instruction += f"\n---\n{task_description}\n---"
      simulator_instruction += """Please output the results of your simulation directly in the format of a real MySQL/Postgres database environment.
      Please note: 
      *1. Do not output the thought process 
      *2. Do not output any interpretation of the results. 
      *3. The subsequent series of interactive commands are logically coherent, and you are asked to keep the logic of the output result data as correct as possible for multiple outputs.
      *4. All results are given as complete strings, with no use of ellipsis."""
      
      client = get_openai_client()
      completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": simulator_instruction},
                {"role": "user", "content": self.specific_task},
            ]
        )
      db_task_response = completion.choices[0].message.content
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
