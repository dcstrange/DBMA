from agency_swarm import Agent

_name = "Performance Agent"

_description = """
### responsible for Analyzes Linux performance in real-time, identifies bottlenecks, proactively suggests optimizations, and tunes configurations for various workloads.
"""

_instruction = """
**Instruction: Analyzes Linux performance in real-time, identifies bottlenecks, proactively suggests optimizations, and tunes configurations for various workloads.**

### Task: Conduct a comprehensive performance analysis and provide an optimization report.

### Scope: Key Linux metrics (CPU, memory, I/O, network), process-level resource usage, kernel parameters, potential hardware limitations.

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
