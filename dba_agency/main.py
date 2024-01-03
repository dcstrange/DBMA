import os
from agency_swarm import Agency
from agency_swarm import Agent
from agency_swarm import set_openai_key

from agents import task_intention
from agents import tot_task
from agents import db_env_proxy
from agents import rag_advance
from agents import toolkit
from agents.experts_team import ExpertTeam


proj_dir = "/home/ubuntu/git/DBMA"
secret_dir = proj_dir + "/secret-configs"
with open(secret_dir + "/OAI_API_KEY") as f:
    os.environ['OPENAI_API_KEY'] = f.read()

set_openai_key(os.environ['OPENAI_API_KEY'])

task_intention = task_intention.create_agent()
tot_task = tot_task.create_agent()
db_env_proxy = db_env_proxy.create_agent()
experts_team = ExpertTeam()

experts_team.add_agent(db_env_proxy)

experts_team_leader = experts_team.get_team_leader()
experts_team_chatgraph = experts_team.get_chat_graph()


chat_graph = [
    task_intention,
    [task_intention, experts_team_leader]
]

chat_graph.extend(experts_team_chatgraph)
for pair in chat_graph:
        if not isinstance(pair, Agent):
            print(f"{pair[0].name} - {pair[1].name}")

agency_manifesto = """
"""

agency = Agency(agency_chart=chat_graph, shared_instructions=agency_manifesto)
agency.demo_gradio(height=900)
