import inspect
import time
from typing import Literal
import json

from agency_swarm.threads import Thread
from agency_swarm.threads import ThreadStatus
from agency_swarm.threads import ThreadProperty

from agency_swarm.agents import Agent
from agency_swarm.messages import MessageOutput
from agency_swarm.user import User
from agency_swarm.util.oai import get_openai_client
from agency_swarm.util.log_config import setup_logging 
logger = setup_logging()

class Session:
    """
    对于一个<sender, recipient> agent pair来说，1个sender.thread只能属于一个Session。可以有多个sender.thread属于不同的session
    """
    
    def __init__(self, caller_agent: Literal[Agent, User], recipient_agent: Agent, caller_thread:Thread=None):
        self.caller_agent = caller_agent
        self.recipient_agent = recipient_agent
        self.client = get_openai_client()
        self.caller_thread = caller_thread
        if isinstance(self.caller_agent, Agent) and self.caller_thread is None:
            raise Exception("Error: initialize Session with Agent as caller must specifiy the parameter caller_thread.")
        self.cached_recipient_threads = []
        self.description = {}
        self.allowed_fails = 5
            
    def get_completion(self, 
                       message:str, 
                       message_files=None, 
                       is_persist: bool=True,
                       yield_messages=True):

        recipient_thread = self._retrieve_thread_of_topic(message) # try to lock the recipient_thread
        if not recipient_thread or recipient_thread.status is not ThreadStatus.Ready:
            recipient_thread = Thread(copy_from=recipient_thread)
            logger.info(f'New THREAD:')

        recipient_thread.status = ThreadStatus.Running
        recipient_thread.session_as_recipient = self
        recipient_thread.properties = ThreadProperty.OneOff if not is_persist else recipient_thread.properties
        if isinstance(self.caller_agent, User):
            recipient_thread.in_message_chain = self.caller_agent.uuid
        else:
            recipient_thread.in_message_chain = self.caller_thread.in_message_chain

        # 向recipient thread发送消息并获取回复
        gen = self._get_completion_from_thread(recipient_thread, message, message_files, yield_messages)
        try:
            while True:
                msg = next(gen)
                #msg.cprint()
                yield msg
        except StopIteration as e:
            response = e.value
        except Exception as e: # 当会话超时，不能释放Thread对象
            logger.info(f"Exception{inspect.currentframe().f_code.co_name}：{str(e)}")
            raise e
            # # TODO:check是否recipient thread有更新消息
        
        # 成功得到recipient回复后，根据recipient thread属性决定如何做后处理
        if recipient_thread.properties is ThreadProperty.OneOff:
            recipient_thread = None # 直接释放recipient thread
            return response
        else: 
            # 保存recipient thread
            # if recipient_thread not in self.cached_recipient_threads:
            #     self.cached_recipient_threads.append(recipient_thread)
            new_history = f"# Message 1:\n {message}\n\n # Message 2:\n{response}\n"
            self._update_task_description(recipient_thread, new_history)
            self.recipient_agent.add_thread(recipient_thread) 
        
        if recipient_thread.properties is ThreadProperty.CoW:
            # TODO: merge to original thread.
            pass

        recipient_thread.in_message_chain = None
        recipient_thread.status = ThreadStatus.Ready
        recipient_thread.session_as_recipient = None
        # Unlock the recipient_thread
        return response

    def _get_completion_from_thread(self, recipient_thread: Thread, message: str, message_files=None, yield_messages=True):

        # Determine the sender's name based on the agent type
        sender_name = "user" if isinstance(self.caller_agent, User) else self.caller_agent.name
        playground_url = f'https://platform.openai.com/playground?assistant={self.recipient_agent._assistant.id}&mode=assistant&thread={recipient_thread.thread_id}'
        logger.info(f'THREAD:[ {sender_name} -> {self.recipient_agent.name} ]: URL {playground_url}')

        if yield_messages:
            yield MessageOutput("text", self.caller_agent.name, self.recipient_agent.name, message)
            
        run = self._run_message(recipient_thread, message, self.recipient_agent, message_files)
        
        while True: # Check state of Assistant AI running in the State-Machine
            # wait until run completes
            while run.status in ['queued', 'in_progress']:
                time.sleep(5)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=recipient_thread.thread_id,
                    run_id=run.id
                )
                logger.info(f"Run [{run.id}] Status: {run.status}")

            # function execution
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                tool_outputs_for_resubmit = []
                for tool_call in tool_calls:
                    if yield_messages:
                        yield MessageOutput("function", self.recipient_agent.name, self.caller_agent.name,
                                            str(tool_call.function))
                    
                    # TODO:这里如果是SendMessage函数，后续会采用创建新Python线程来执行，需要修改处理逻辑。
                    output = self._execute_tool(tool_call, caller_thread=recipient_thread)
                    if inspect.isgenerator(output):
                        try:
                            while True:
                                item = next(output) # 可能会抛出超时异常(Error Code: 400)
                                if isinstance(item, MessageOutput) and yield_messages:
                                    yield item
                        except StopIteration as e:
                            output = e.value
                            #logger.info(output)
                        except Exception as e:
                            logger.info(f"Exception{inspect.currentframe().f_code.co_name}：{str(e)}")
                            raise e
                    else:
                        if yield_messages:
                            yield MessageOutput("function_output", tool_call.function.name, self.recipient_agent.name,
                                                output)

                    tool_outputs.append({"tool_call_id": tool_call.id, "output": str(output)})
                    tool_outputs_for_resubmit.append({"tools_calls": tool_call.model_dump_json(), "output":str(output)})
                # submit tool outputs
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=recipient_thread.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                except Exception as e:
                    # ☑️[DONE]: 需要考虑提交tool结果是否会失败。例如因为tool执行时间过长，run被自动关闭。这时候需要重新执行run并提交上次结果。
                    # 由于调用自定义Funtion超时，导致RUN进入expired状态后无法提交Funtion执行结果。但由于目前AssistantAPI不支持编辑RUN’step，这就无法做到断点续传。因此一个妥协的办法是将函数的执行结果包装成提示词消息追加到Thread中，然后再re-RUN。

                    logger.info(f"Exception{inspect.currentframe().f_code.co_name}：{str(e)}")
                    logger.info(f"Resubmit the expired tool's output with RUN's information. See: run_id: {run.id}, thread_id: {recipient_thread.thread_id} ...")
                    # Step 1. 获取失败的RUN'step
                    # run_steps = self.client.beta.threads.runs.steps.list(
                    #     thread_id=recipient_thread.thread_id,
                    #     run_id=run.id,
                    #     limit=1,
                    #     order="desc"
                    # )
                    # fail_step = run_steps._get_page_items()[0]
                    
                    # Step 2. 将失败step的信息和tool的返回值打包成新的提示词
                    wapper_output = self._wapper_expired_tool_output(str(tool_outputs_for_resubmit))
                    logger.info(wapper_output)
                    
                    # Step 3. 新的提示词追加到Thread中，并重新执行
                    run = self._run_message(recipient_thread, wapper_output, self.recipient_agent, message_files)
                    
            # error
            elif run.status == "failed":
                logger.info("Run Failed. Error: ", run.last_error)
                if self.allowed_fails > 0:
                    time.sleep(5)
                    logger.info(f"Retry run the thread:[{recipient_thread.thread_id}] on assistant:[{self.recipient_agent.id}] ... ")
                    run = self._run(recipient_thread, self.recipient_agent) # try again.
                    self.allowed_fails -= 1
                else:
                    raise Exception("Run Failed. Error: ", run.last_error)
            elif run.status == "expired":
                logger.info("Run expired. Error: ", run.last_error)
                if self.allowed_fails > 0:
                    time.sleep(5)
                    logger.info(f"Retry run the thread:[{recipient_thread.thread_id}] on assistant:[{self.recipient_agent.id}] ... ")
                    run = self._run(recipient_thread, self.recipient_agent) # try again.
                    self.allowed_fails -= 1
                else:
                    raise Exception("Run Failed. Error: ", run.last_error)
            # return assistant message
            else:
                messages = self.client.beta.threads.messages.list(
                    thread_id=recipient_thread.thread_id
                )
                message = messages.data[0].content[0].text.value

                if yield_messages:
                    yield MessageOutput("response_text", self.recipient_agent.name, self.caller_agent.name, message)

                return message

    def _run_message(self, thread:Thread, message:str, agent:Agent, message_files=None):
        # create message
        self.client.beta.threads.messages.create(
            thread_id=thread.thread_id,
            role="user",
            content=message,
            file_ids=message_files if message_files else [],
        )
        # create run
        run = self.client.beta.threads.runs.create(
            thread_id=thread.thread_id,
            assistant_id=agent.id,
        )
        return run
    
    def _run(self, thread:Thread, agent:Agent):
        run = self.client.beta.threads.runs.create(
            thread_id=thread.thread_id,
            assistant_id=agent.id,
        )
        return run
    
    def _retrieve_thread_of_topic(self, message:str) -> Thread:
        classifier_instruction = """
        You are the expert responsible for understanding session scenarios. A session consists of several characters discussing a task, the process of performing it, and the intermediate results. You will receive a list of generalized descriptions of multiple sessions, each of which includes information such as: task context, content, goals, current status, existing results, unknown results. Finally, You will receive a new statement from one of the characters. Your task is to choose the session from the list of session descriptions that is most appropriate for that new statement to join, and give reasons why.
        Output the results in the following json format.
        {
            "session_id": ...,
            "reason": "..."
        }
        In this json, give the session id (integer) and reason (string) why the new statement should be joined and the reason for not joining another session. If you think that the new statement cannot join to any existing session, "session_id" will be set to -1. 
        Must not include any characters other than json in the output.
        """    

        sessions_decription = ""
        for index, thread in enumerate(self.recipient_agent.threads, start=1):
            sessions_decription += f"### Description of Session {index}:\n{thread.task_description}\n\n"
            
        if not sessions_decription:
            return None
        
        # sessions_decription += f"### new statement\n{self.recipient_agent.name}:{message}"
        
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": classifier_instruction},
                {"role": "user", "content": sessions_decription},
                {"role": "user", "content": f"### new statement\n{self.recipient_agent.name}:{message}"},
            ]
        )
        response = completion.choices[0].message.content
        
        # Logging
        if isinstance(self.caller_agent, User):
            caller_name = "User"
        else:
            caller_name = self.caller_agent.name
        log_header = f"retrieve one from {len(self.recipient_agent.threads)} sessions that {caller_name} → {self.recipient_agent.name}...\n"
        logger.info(log_header + response)
        
        #
        thread_json = json.loads(response)
        session_id = thread_json["session_id"]
        if session_id <= 0:
            return None
        else:
            return self.recipient_agent.threads[session_id - 1]
                
    def _update_task_description(self, thread:Thread, new_history:str):
        # Generate the description of this session at this state. 
        # instruction大意：requires clarity and conciseness.
        # 如果description为空，则根据json中每个字段的描述生成decription。如果非空，则根据新历史来更新description。
        # 更新方法如下：
        # 只需要修改"existing results"和"unknown results"。 
        # 分析最近产生的会话消息中是否存在"existing results"字段中未收录的最新的结果，如果有，则加入填入字段。同时，删除"unknown results"字段中对应的元素（如果有）。
        # 分析最近产生的会话消息中是否存在"unknown results"字段中未收录的待获取的结果，如果有，则填土该字段。   
        
        instruction = """You are an expert on understanding and analyzing complex task session and you are responsible for generating a description of the task based on its session history. The description of the task session must be output in the following json format, which gives the fields required to be output and the detailed requirements for each field.
        
        {
            "backgroud": "Extract the context of the task from the first message of session history and briefly summarize it in one sentence", 
            "task_content": "Define clear and specific criteria based solely on the first message that indicate the task content is complete, focusing on the direct deliverables or outcomes requested.", 
            "completion conditions": "Define clear and specific criteria based solely on the first message that indicate the task content is complete, focusing on the direct deliverables or outcomes requested.", 
            "existing results": "Extract and *qualitatively summarize the (intermediate) results that have been produced by this task from the session history, and output them as a bulleted list.", 
            "unknown results": "Based on the principle of the 'completion conditions' field, the (intermediate) results required by the task but not yet obtained are extracted from the session history and output as a bulleted list",
            "status": "Analyze from the session history and the results what is the task status according to the completion condition, e.g., completed, uncompleted, unable to complete, uncertained etc."
        }
        
        You will receive a task's recent session history and an existing description of the task's session, labeled with ####, respectively. Follow the steps below to output a new session description:
        1. if description is empty, generate a description that strictly adheres to the requirements of each field in the json.
        2. otherwise, update the "existing results" and "unknown results" fields in the description according to the new session history. The update method is:
            - Analyze the most recent generated session messages for the presence of the latest (intermediate) results that are not included in the "existing results" field, and if so, populate the field. At the same time, delete the corresponding element (if any) in the "unknown results" field.
            - Analyze the most recently generated session messages for any pending results that are not included in the "unknown results" field, and if so, populate the field.

        Note that your description is required to be clear and unambiguous, and your final output cannot contain any characters other than the description in json format.
        """
        
        message = f"### Description of Task Session:\n{thread.task_description}"
        message += f"\n ### Recent Task Session History:\n{new_history}"

        
        completion = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": message},
            ]
        )
        task_description = completion.choices[0].message.content
        
        if isinstance(self.caller_agent, User):
            log_header = f"Updated the task description of the session that User → {self.recipient_agent.name}:[{thread.thread_id}]...\n"
        else:
            log_header = f"Updated the task description of the session that {self.caller_agent.name}:[{self.caller_thread.thread_id}] → {self.recipient_agent.name}:[{thread.thread_id}]...\n"

        logger.info(log_header + task_description)
        thread.task_description = task_description
        return task_description

    def _execute_tool(self, tool_call, caller_thread:Thread):
        funcs = self.recipient_agent.functions
        func = next((func for func in funcs if func.__name__ == tool_call.function.name), None)

        if not func:
            return f"Error: Function {tool_call.function.name} not found. Available functions: {[func.__name__ for func in funcs]}"

        try:
            # init tool
            func = func(**eval(tool_call.function.arguments))
            func.caller_agent = self.recipient_agent
            # get outputs from the tool
            output = func.run(caller_thread)

            return output
        except Exception as e:
            error_message = f"Error: {e}"
            if "For further information visit" in error_message:
                error_message = error_message.split("For further information visit")[0]
            return error_message

    def _wapper_expired_tool_output(self, output:str) -> str:
        """
        - 处理issues：由于调用自定义Funtion超时，导致RUN进入expired状态后无法提交Funtion执行结果。
        - 但由于目前AssistantAPI不支持编辑RUN’step，这就无法做到断点续传。因此一个妥协的办法是将函数的执行结果包装成提示词消息追加到Thread中，然后再re-RUN。
        """
        wapper = f""" We have executed the following steps:
        ---
        {output}
        ---
        keep going on.
        """
        return wapper

# Example usage within this file
if __name__ == "__main__":
    from agency_swarm import set_openai_key
    from getpass import getpass
    set_openai_key(getpass("Please enter your openai key: "))

    agent1 = Agent(name="agent1",
                     tools=None,
                     description="description",
                     instructions="description",
                     files_folder=None)
    agent2 = Agent(name="agent2",
                     tools=None,
                     description="description",
                     instructions="description",
                     files_folder=None)
    agent1.init_oai()
    agent2.init_oai()
    sender_thread = Thread()
    session = Session(agent1, agent2,sender_thread)
    session.get_completion("hello world.", topic="hello",is_persist=True)
    