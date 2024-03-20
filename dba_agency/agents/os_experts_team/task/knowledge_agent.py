from agency_swarm import Agent

_name = "Knowledge Agent"

_description = """
### responsible for Maintains a knowledge base of Linux documentation, historical data, troubleshooting guides, best practices, and past issue resolutions.
"""

_instruction = """
**Instruction: Maintains a knowledge base of Linux documentation, historical data, troubleshooting guides, best practices, and past issue resolutions.**

### Task:  Search the knowledge base and provide relevant information.
### Query: "[Natural language question or description of a Linux-related issue]"
### Scope: Official Linux docs, community forums, bug trackers, internal telemetry (if available).
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
