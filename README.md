![Framework](./framework.png)

# 待完成功能

## 🔥High Priority

- [ ] 初步构建一个Agency for DBA
- [ ] Agent Wait preparation机制。例如Team Leader需要等待并汇总（根据某个任务列表）所有Experts的任务意见后，再定夺下一步行动。这样的决策质量可能会更高，降低由于信息不全导致的决策失误。

## 🧊Low Priority
- [ ] 持续更新Agent知识。最直接的方法是更新RAG。**Continuous Learning**:
    - After each interaction, review the accuracy of your topic categorization.
    - Continuously refine your keyword and phrase recognition patterns based on user feedback and evolving database management trends.

- [ ] 在与DB环境交互的部分，后续使用真实功能替换（低优先级），包括Toolkits Agent，Data Analyzer等
- [ ] 当前Agency-Swarm框架中Agent间沟通的**目的**是“问答”（且单向），这种单一目的的交流方式限制了Agency任务能力。后续考虑在Agency-Swarm底层追加其他目的形式的沟通方式，例如某个Agent有自己的主线任务，它通过其它Agent那里获取消息来不断思考自己的任务。

## ✅Finished

# 待解决工程问题

## 🔥High Priority
- [ ] [Agency-Swarm related] Print所有Agent设定，用于观测issue和Benchmark log

- [ ] 自定义更多功能的SendMessage函数。当前SendMessage函数属于通用内同CoT的提示词。但针对不同目的对话，使用自定义的SendMessage可能会更好。

- [ ] 考虑运行时自主修改（增删改）Assistant Instruction，可根据任务的执行状态自动优化Assistant和MA结构。

- [ ] 将专家团Expert Team打包成另一个Agency，可能由Team Leader Agent作为对外接口。整个架构是由多个主题的Agencies组成。

- [ ] 由于Function call时间过长导致OpenAI会话过期。怎么解决？
  - openai.BadRequestError: Error code: 400 - {'error': {'message': 'Runs in status "expired" do not accept tool outputs.', 'type': 'invalid_request_error', 'param': None, 'code': None}}


## 🧊Low Priority

- [ ] 【AgencySwarm Issue】目前AgencySwarm的Agent间交流机制是同步版本，从root agent (CEO) 开始，<u>递归的</u>调用相关Agent的SendMessage函数。虽然在AgencySwarm抽象出了CommunicationThread对象（见`agency_swarm\threads\thread.py`），即每个pair <sender agent, recipient agent> 所对应的上下文，但所有的Thread对象在单线程中被串行执行，而且消息回复仅仅是简单的function return。后面需要改成多线程，异步版本。备注：当前版本是通过`Thread._execute_tool(thread.self, self.recipient_agent.SendMessage())`来attach到新的CommunicationThread上下文的。
  - 修改思路：每个Agent的实现为一个系统线程，Agent实例包含着对应Assitant环境，和由self作为message Sender的所有会话（Session）。我们使用Session替换掉CommunicationThread，因为CommunicationThread对象实在单线程中被Agency全局管理，Session由Agent线程自己管理。这样消息发送/回复的机制就可以是REST接口了。
  
  - AgencySwarm原始方案
  <img src="./figures/tmp437D.png" alt="image-20231226143945843" style="zoom: 25%;" /> <img src="./figures/tmpA15E.png" alt="image-20231226143945843" style="zoom: 25%;" />

## ✅Finished

- 实现伪DB交互环境
  - 实现在DBMA/db_pseudo_env目录中。包含着一个伪DB环境Web Server，和向伪DB环境发送任务消息的Client。使用命令`python db_pseudo_env/db_pseudu_env_server.py`启动伪DB环境Server，并访问 http://localhost:5000/task 查看任务并手动输入任务执行结果。

# 待研究难题

## 🔥High Priority

- [ ] 提示词工程：如何为Agent角色化提供初始Instruction，促使任务高质量推进。Instruction需要考虑以下方面 （参考：LMOps）

  - 动作细节

  - 接收者非人类，而是Agent

  - 输出的一致性

  - 输出的丰富性
- [ ] 任务规划：ToT技术。如何在以自然语言作为任务的场景中使用ToT技术。需要考虑两方面：
  - 开放的任务描述 → 有限的Action
  - 为Action打分，eg, UCT

- [ ] 任务回溯技术。在一个Thread中的任务执行中遇到任务失败时候，需要回溯到上一个分叉节点重新规划路径。那么就需要重新整理这段失败路径上所有参与讨论的Agent的Memory。如何选择上一个分叉节点，如何整理失败经验重新执行任务需要解决。（世杰）

- [ ] **思考如何构造测试benchmark来测试每次升级后MA结构的表现。包括测试用例、数据模型等**

# 🛠️相关技术

## AlphaZero

[Mastering the game of Go with deep neural networks and tree search | Nature](https://www.nature.com/articles/nature16961)

[Mastering the game of Go without human knowledge | Nature](https://www.nature.com/articles/nature24270)

[AlphaZero: Shedding new light on chess, shogi, and Go - Google DeepMind](https://deepmind.google/discover/blog/alphazero-shedding-new-light-on-chess-shogi-and-go/)



## LMOps

[microsoft/LMOps: General technology for enabling AI capabilities w/ LLMs and MLLMs (github.com)](https://github.com/microsoft/LMOps)

https://www.promptingguide.ai/

## Instructor

[jxnl/instructor: structured outputs for llms (github.com)](https://github.com/jxnl/instructor)



## ToT/CoT

| Paper                                                        | Topic                                                        | Summary                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Self-Consistency Improves Chain of Thought Reasoning in Language Models | expand CoT                                                   | CoT的一个完善，简单来说，就是对于一个任务采用多个CoT，最后让所有的CoT进行投票，票数最多结果作为输出 |
| Tree of Thoughts: Deliberate Problem Solving with Large Language Models | ToT,Long Reasoning                                           | 介绍了CoT的不足之处，以sum24，创意写作为实例介绍了ToT的基本思想以及内容 |
| Large Language Model Guided Tree-of-Thought                  | ToT System,Long Reasoning                                    | 以数独游戏为示例，设计了一个具体的ToT system来指导LLM完成较难的任务 |
| Reasoning with Language Model is Planning with World Model   | Reasoning via planning,LLM for Planning,Monte Carlo Tree Search | 文中提出了一个world-model，将任务的解决规划成state0->action0->state1->action1->......根据采取行动后的state来评估action的价值，从而更好地选取action，同时引入奖励机制利用MCTS的方法来进行action空间搜索，从而进行任务规划，该方法在任务规划，长数学推理，长逻辑推理方面都有较好的表现，（DB-GPT中的根因分析就是基于该部分做的） |
| Automatic Chain of Thought Prompting in Large Language Models | Auto CoT                                                     |                                                              |

