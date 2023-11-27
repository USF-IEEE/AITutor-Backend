from AITutor_Backend.src.BackendUtils.sql_serialize import *
from AITutor_Backend.src.BackendUtils.json_serialize import *
from collections import deque

class ChatHistory(SQLSerializable, JSONSerializable):
        def __init__(self,):
            super(ChatHistory, self).__init__()
            self.chat = deque(["AI Tutor:\nHey I am your AI Tutor. How can I help you today?",])
        def hear(self, user_prompt,):
            """Adds a User Chat to the history
            
            Args:
                user_prompt (str)
            """
            # if len(self.chat) > 10: self.chat.popleft()
            self.chat.append(f"\Student:\n{user_prompt}")
            
        def respond(self, tutor_response):
            """Adds a Tutor Chat to the history
            
            Args:
                tutor_response (str)
            """
            # if len(self.chat) > 10: self.chat.popleft()
            self.chat.append(f"\nAI Tutor:{tutor_response}")
            
        def env_string(self,):
            """returns environment formatted string.

            Returns:
                str: environment formatted string of chat history
            """
            return "\n".join(list(self.chat)[-12::])
        @staticmethod
        def from_sql(chat_history, ):
            """Recreates a Chat History from an SQL value

            Args:
                chat_history (str): \'[SEP]\'  Serialized version of Chat History.
            """
            chat_ref = ChatHistory()
            chat_ref.chat = deque((chat_history.split("[SEP]")))
            return chat_ref
            
        def to_sql(self,) -> str:
            """Serializes a Chat History for SQL

            Returns:
                str: Chat History
            """
            return "[SEP]".join(self.chat)
        
        def format_json(self,):
            return {"chat": "\n".join(self.chat)}
                    