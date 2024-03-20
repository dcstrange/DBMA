from typing import List
from agency_swarm import Agent

from . import dev_team_leader
from . import authority_controller
from . import sys_admin

class ExpertTeam:
    
    def __init__(self):
        self.manifesto = "" ""
        self.team_leader = dev_team_leader.create_agent()
        self.chat_graph = []
        self.team = [
            self.team_leader,
            authority_controller.create_agent(),
            sys_admin.create_agent()
        ]
        for i in range(len(self.team)):
            for j in range(len(self.team)):
                if i != j:
                    self.chat_graph.append([self.team[i], self.team[j]])

    def get_team_leader(self) -> Agent:
        return self.team_leader

    def get_team(self) -> List[Agent]:
        return self.team

    def get_chat_graph(self) -> List:
        return self.chat_graph

    def add_agent(self, agent:Agent):
        self.team.append(agent)
        self.chat_graph.clear()
        for i in range(len(self.team)):
            for j in range(len(self.team)):
                if i != j:
                    self.chat_graph.append([self.team[i], self.team[j]])



if __name__ == "__main__":
    import os
    proj_dir = "/home/ubuntu/git/DBMA"
    secret_dir = proj_dir + "/secret-configs"
    with open(secret_dir + "/OAI_API_KEY") as f:
        os.environ['OPENAI_API_KEY'] = f.read()

    from agency_swarm import set_openai_key
    set_openai_key(os.environ['OPENAI_API_KEY'])
    team = ExpertTeam()
    graph = team.get_chat_graph()
    for pair in graph:
        print(f"{pair[0].name} - {pair[1].name}")