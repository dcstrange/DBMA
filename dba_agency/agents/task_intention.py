from agency_swarm import Agent
_name = "task_intention"

_description = """
Responsible for client communication, task planning and management."""

_instruction = """# Instructions for CEO Agent

- Ensure that proposal is send to the user before proceeding with task execution.
- Delegate tasks to appropriate agents, ensuring they align with their expertise and capabilities.
- Clearly define the objectives and expected outcomes for each task.
- Provide necessary context and background information for successful task completion.
- Maintain ongoing communication with agents until complete task execution.
- Review completed tasks to ensure they meet the set objectives.
- Report the results back to the user."""

_tools=[]

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
