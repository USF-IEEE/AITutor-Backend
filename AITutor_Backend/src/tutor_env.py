from enum import IntEnum
from AITutor_Backend.src.TutorUtils.notebank import *


class TutorEnv:
    class ChatHistory:
        def __init__(self,):
            self.chat = ["AI Tutor:\nHey I am your AI Tutor. How can I help you today?",]
        def hear(self, user_prompt,):
            self.chat += [f"\nUser:\n{user_prompt}"]
        def respond(self, tutor_response):
            self.chat += [f"\nAI Tutor:{tutor_response}"]
        def env_string(self,):
            """returns environment formatted string.

            Returns:
                str: environment formatted string of chat history
            """
            return "\n".join(self.chat)
                 
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
            self.chat_history = TutorEnv.ChatHistory()
            States = [[self.__prompt_start, ], # Prompting States
                [], # Teaching States
                [], # Guiding States
                [] # Testing States
            ]
            
        def __load_prompt(self, prompt_file, kwargs*):
            # Open File:
            with open(prompt_file, 'r') as f:
                prompt_string = f.read()

            # Replace Values in Prompt:
            for k, v in kwargs.items():
                prompt_string = self.prompt_string.replace(k, v)

            # Return Prompt:
            return prompt_string
        
        def __prompt_reflect(self, prompt):
            current_prompt = """Using the Notebank operations described above and based on the current chat history with the user, reflect and modify the Notebank according to the users specific goals as a learner:"""
            chat_history = self.chat_history.env_string()
            notebank_state = self.notebank.env_string()
            
            
        
        def process_action(self, user_input):
            """Processes user input and returns new state and Tutor Actions

            Args:
                user_input (Dict[str, any]): JSON data from user
            """
            if user_input.get("is_audio", False): # User Data is Audio
                pass
                # TODO: user_input["user_prompt"] = self.__ears.hear(user_input["user_prompt"]) 
                
            user_prompt = user_input["user_prompt"]