from typing import List
from agency_swarm import Agent

from . import team_leader
from . import expert_troubleshooting
from . import expert_data_modeling
from . import expert_migration
from . import expert_monitor
from . import expert_perf_tuning
from . import expert_security
from . import expert_recovery
from . import expert_scaling

class ExpertTeam:
    
    def __init__(self):
        self.manifesto = "" ""
        self.team_leader = team_leader.create_agent()
        self.chat_graph = []
        self.team = [
            self.team_leader,
            expert_scaling.create_agent(),
            expert_recovery.create_agent(),
            expert_security.create_agent(),
            expert_perf_tuning.create_agent(),
            expert_monitor.create_agent(),
            expert_migration.create_agent(), 
            expert_data_modeling.create_agent(),
            expert_troubleshooting.create_agent()
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