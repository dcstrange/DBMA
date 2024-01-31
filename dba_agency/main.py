import os
from pathlib import Path
from getpass import getpass

project_root = Path(__file__).parent.parent.absolute()
os.environ['AS_PROJECT_ROOT'] = str(project_root)
print("Project root set to:", os.environ['AS_PROJECT_ROOT'])

from agency_swarm import setup_logging # os.environ['AS_PROJECT_ROOT'] where the log dir is created
logger = setup_logging()
logger.info('This is a debug message')


from agency_swarm import Agency
from agency_swarm import Agent
from agency_swarm import set_openai_key

from agents import task_intention
from agents import tot_task
from agents import db_env_proxy
from agents import rag_advance
from agents import toolkit
from agents import experts_team
from agents.experts_team import ExpertTeam

secret_file_path = os.path.join(project_root, 'secret-configs', 'OAI_API_KEY')
with open(secret_file_path) as f:
    if f:
        os.environ['OPENAI_API_KEY'] = f.read()
    else:
        os.environ['OPENAI_API_KEY'] = getpass("Please enter your openai key:")
set_openai_key(os.environ['OPENAI_API_KEY'])


task_intention = task_intention.create_agent()
tot_task = tot_task.create_agent()
db_env_proxy = db_env_proxy.create_agent()
experts_team = ExpertTeam()

#experts_team.add_agent(db_env_proxy)

experts_team_leader = experts_team.get_team_leader()
experts_team_chatgraph = experts_team.get_chat_graph()


chat_graph = [
    task_intention,
    [task_intention, experts_team_leader]
]

channels_db_env = []
experts_team_agents = experts_team.get_team()
for agent in experts_team_agents:
     channels_db_env.append([agent, db_env_proxy])
channels_db_env.remove([experts_team_leader, db_env_proxy])


chat_graph.extend(experts_team_chatgraph)
chat_graph.extend(channels_db_env)

for pair in chat_graph:
        if not isinstance(pair, Agent):
            print(f"{pair[0].name} - {pair[1].name}")

agency_manifesto = """
"""

agency = Agency(agency_chart=chat_graph, shared_instructions=agency_manifesto)
agency.demo_gradio(height=900)
