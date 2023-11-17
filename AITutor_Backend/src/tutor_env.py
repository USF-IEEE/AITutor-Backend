from enum import IntEnum
from collections import deque
from AITutor_Backend.src.TutorUtils.notebank import *
from AITutor_Backend.src.TutorUtils.chat_history import *
from AITutor_Backend.src.BackendUtils.sql_serialize import *

class TutorEnv(SQLSerializable,):
    class States(IntEnum):
            PROMPTING=0
            TEACHING=1
            GUIDING=2
            TESTING=3
    class Executor(SQLSerializable,):
        
        
        def __init__(self, env:'TutorEnv', ):
            super(TutorEnv.Executor, self).__init__()
            self.env = env
            self.__ears = None # TODO: Add whisper-3 api
            self.__mouth = None # TODO: Add 
            self.__brain = None # TODO: Add LLM API Reference
            
        
        def process_action(self, user_input):
            """Processes user input and returns new state and Tutor Actions

            Args:
                user_input (Dict[str, any]): JSON data from user
                
            Returns:
                new_state: data to return to the user
                current_env_state: enum value which iterates through the environment states
            """
            if user_input.get("is_audio", False): # User Data is Audio
                pass
                # TODO: user_input["user_prompt"] = self.__ears.hear(user_input["user_prompt"]) 
            
            user_prompt = user_input["user_prompt"]
            # TODO: Do processing
            self.env.chat_history.hear(user_prompt)
            self.States[self.env.current_state](user_input)
            
            
    def __init__(self,):
        """ Creates base TutorEnv
        
        TutorEnv has a:
            - notebank
            - chat history
            - executor
            - concept database
            - Slide Planner TODO: implement
            - Question Suite TODO: implement
            
        """
        super(TutorEnv, self).__init__()
        self.current_state = 0 # Prompt Start
        self.notebank = NoteBank()
        self.chat_history = ChatHistory()
        self.concept_database = None
        self._has_concept_database = False
        self.States = [
                None,# Prompting States TODO: Change to be a Ptr to Prompter 
                None, # Teaching States
                None, # Guiding States
                None  # Testing States
            ]
    
    def step(self, input_data):
        return {"error": "TODO: implement Logic"}, -1
        
    
    ## Data Functions:
    @staticmethod
    def from_sql(current_state, notebank_state, chat_history):
        """Recreates a Chat History from an SQL value

        Args:
            chat_history (str): \'[SEP]\'  Serialized version of Chat History.
        """
        tutor_ref = TutorEnv()
        tutor_ref.current_state = current_state
        tutor_ref.notebank = NoteBank.from_sql(notebank_state)
        tutor_ref.chat_history = ChatHistory.from_sql(chat_history)
        return tutor_ref
            
    def to_sql(self,) -> str:
        """Serializes a Chat History for SQL

        Returns:
            str: Chat History
        """
        return self.current_state
        
            