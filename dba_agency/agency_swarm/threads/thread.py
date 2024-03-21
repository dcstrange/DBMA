from agency_swarm.util.oai import get_openai_client

from enum import Enum

class ThreadStatus(Enum):
    Running = "Running"
    Ready = "Ready"

class ThreadProperty(Enum):
    Persist = "Persist"
    OneOff = "One-Off"
    CoW = "Copy on Write"


class Thread:
    def __init__(self, thread_id: str=None, copy_from=None):
        self.client = get_openai_client()
        self.thread_id: str = thread_id
        self.openai_thread = None
        self.instruction: str = None
        self.in_message_chain: str = None
        self.status: ThreadStatus = ThreadStatus.Ready
        self.properties: ThreadProperty = ThreadProperty.Persist
        self.sessions = {} # {"recipient agent name", session}
        self.session_as_sender = None    # 用于python线程异常挂掉后的处理
        self.session_as_recipient= None # 用于python线程异常挂掉后的处理
        self.task_description = ""
        
        if self.thread_id:
            self.openai_thread = self.client.beta.threads.retrieve(self.thread_id)
        else:
            self.openai_thread = self.client.beta.threads.create()
            self.thread_id = self.openai_thread.id
        if copy_from is not None:
            # TODO: copy all message from a existed thread
            pass

    def _dump_info(self):
        pass