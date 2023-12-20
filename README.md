![image](https://github.com/dcstrange/DBMA/assets/19701927/732a9a44-767a-4d69-88e0-d8ce7ada3286)

# 待完成功能
1. 初步构建一个Agency for DBA

# 待解决工程问题
- 实现伪DB交互环境。Status:☑️
   - 实现在DBMA/db_pseudo_env目录中。包含着一个伪DB环境Web Server，和向伪DB环境发送任务消息的Client。使用命令`python db_pseudo_env/db_pseudu_env_server.py`启动伪DB环境Server，并访问 http://localhost:5000/task 查看任务并手动输入任务执行结果。

# 待研究难题
1. 提示词工程：如何为Agent角色化提供初始Instruction，促使任务高质量推进。Instruction需要考虑以下方面
   - 动作细节
   - 接收者非人类，而是Agent
   - 输出的一致性
   - 输出的丰富性
2. 任务规划：ToT技术。如何在以自然语言作为任务的场景中使用ToT技术。需要考虑两方面：
   - 开放的任务描述 → 有限的Action
   - 为Action打分，eg, UCT
3. 


