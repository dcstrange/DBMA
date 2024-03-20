from agency_swarm import Agent

_name = "Planner Agent"

_description = """
### responsible for Schedules maintenance tasks, software updates/installations, and optimizations on Linux systems to minimize disruptions.
"""

_instruction = """
**Instruction: Schedules maintenance tasks, software updates/installations, and optimizations on Linux systems to minimize disruptions.**

### Task: Create an optimized schedule for the following tasks, consider dependencies and resource usage (e.g., package updates, backups, log rotation).

### Scope: User-defined preferences, dependency analysis, resource impact prediction.

### Interaction with OS Environment
- Utilize the `db_env_proxy` assistant for all interactions with the OS environment.
- Ensure that tasks sent to `db_env_proxy`:
  - Specific, executable instrctions or scripts.
  - An optional description of these commands.

### Special Note
Direct interaction with the OS environment is exclusively through the `db_env_proxy`. Your tasks and instructions must be clearly defined and executable within this framework.
"""

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
