from enum import IntEnum
from AITutor_Backend.src.TutorUtils.notebank import *
from AITutor_Backend.src.TutorUtils.chat_history import ChatHistory

class TutorEnv:  
    class Executor:
        class States(IntEnum):
            PROMPTING=0
            TEACHING=1
            GUIDING=2
            TESTING=3
        
        def __init__(self, env:"Executor", ):
            self.env = env
            self.__ears = None # TODO: Add whisper-3 api
            self.__mouth = None # TODO: Add 
            self.__brain = None # TODO: Add LLM API Reference
            self.current_state = (0, 0) # Prompt Start
            self.notebank = NoteBank()
            self.chat_history = ChatHistory()
            States = [[self.__prompt_start, ], # Prompting States
                [], # Teaching States
                [], # Guiding States
                [] # Testing States
            ]
            
        
        def process_action(self, user_input):
            """Processes user input and returns new state and Tutor Actions

            Args:
                user_input (Dict[str, any]): JSON data from user
            """
            if user_input.get("is_audio", False): # User Data is Audio
                pass
                # TODO: user_input["user_prompt"] = self.__ears.hear(user_input["user_prompt"]) 
            
            user_prompt = user_input["user_prompt"]
            # Add to chat history:
            self.chat_history.hear(user_prompt)