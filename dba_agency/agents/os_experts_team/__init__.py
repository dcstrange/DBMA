from agency_swarm import Agent
from typing import List

from . import os_team_leader
from .module import expert_memory
from .module import expert_io
from .module import expert_networking
from .module import expert_schedualing
from .module import expert_driver
from .module import expert_filesystem
from .module import expert_storage_device
from .module import expert_cpu
from .module import expert_gpu

from .task import performance
from .task import diagnostician
from .task import security
from .task import planner
from .task import knowledge_agent
from .task import foresighter


class OSTeam:
    def __init__(self):
        self.manifesto = "" ""
        self.team_leader = os_team_leader.create_agent()
        self.chat_graph = []
        self.team = [
            self.team_leader,
            performance.create_agent(),
            diagnostician.create_agent(),
            security.create_agent(),
            planner.create_agent(),
            # knowledge_agent.create_agent(),
            # foresighter.create_agent()
            # expert_memory.create_agent(),
            # expert_io.create_agent(),
            # expert_networking.create_agent(),
            # expert_schedualing.create_agent(),
            # expert_driver.create_agent(),
            # expert_filesystem.create_agent(),
            # expert_storage_device.create_agent(),
            # expert_cpu.create_agent(),
            # expert_gpu.create_agent(),
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