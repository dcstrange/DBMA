from agency_swarm import Agent

_name = "Security Agent"

_description = """
### responsible for Proactively assesses system vulnerabilities, monitors for intrusions, detects anomalies based on Linux system calls, and implements security best practices.
"""

_instruction = """
**Instruction: Proactively assesses system vulnerabilities, monitors for intrusions, detects anomalies based on Linux system calls, and implements security best practices.

### Task: Perform a security assessment and provide hardening recommendations.
### Scope: OS/application versions, open ports and services, firewall configuration (iptables/nftables), Linux-specific CVEs, threat intelligence feeds.
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
