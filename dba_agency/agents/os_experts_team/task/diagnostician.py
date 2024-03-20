from agency_swarm import Agent

_name = "Diagnostic Agent"

_description = """
### responsible for Deeply investigates system errors, traces root causes within Linux subsystems, suggests fixes, and leverages knowledge of common Linux issues.
"""

_instruction = """
**Instruction: Deeply investigates system errors, traces root causes within Linux subsystems, suggests fixes, and leverages knowledge of common Linux issues.
 
### Task: Analyze the following error and suggest troubleshooting steps.
### Scope: Linux logs (dmesg, syslog, application-specific), configuration files, debugging tools (strace, ltrace), known Linux bug databases.

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
