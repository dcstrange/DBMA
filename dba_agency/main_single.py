import os
from pathlib import Path
from getpass import getpass

project_root = Path(__file__).parent.parent.absolute()
os.environ['AS_PROJECT_ROOT'] = str(project_root)
print("Project root set to:", os.environ['AS_PROJECT_ROOT'])

from agency_swarm import setup_logging # os.environ['AS_PROJECT_ROOT'] where the log dir is created
logger = setup_logging()
logger.info('This is a debug message')

from agency_swarm import set_openai_key
secret_file_path = os.path.join(project_root, 'secret-configs', 'OAI_API_KEY')
with open(secret_file_path) as f:
    if f:
        os.environ['OPENAI_API_KEY'] = f.read()
    else:
        os.environ['OPENAI_API_KEY'] = getpass("Please enter your openai key:")
set_openai_key(os.environ['OPENAI_API_KEY'])

from agency_swarm import Agency
from agency_swarm import Agent

from agents import single_solver
from agents.experts_team import ExpertTeam

single_solver = single_solver.create_agent()

#experts_team.add_agent(db_env_proxy)

chat_graph = [
    single_solver,
    []
]

agency_manifesto = """
"""

agency = Agency(agency_chart=chat_graph, shared_instructions=agency_manifesto)
agency.demo_gradio(height=1800)
