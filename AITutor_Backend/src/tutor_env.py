from enum import IntEnum
from collections import deque
from AITutor_Backend.src.TutorUtils.notebank import *
from AITutor_Backend.src.TutorUtils.chat_history import *
from AITutor_Backend.src.BackendUtils.sql_serialize import *
from AITutor_Backend.src.TutorUtils.prompts import Prompter, PromptAction
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase
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
            
            if self.env.current_state == int(TutorEnv.States.PROMPTING):
                prompt_obj, terminate = self.env.prompter.perform_tutor(user_prompt)
                if terminate:
                    main_concept = None
                    for note in self.env.notebank.get_notes():
                        if "main concept:" in note.lower():
                            note = note[note.lower().index("main concept:"):].strip()
                            main_concept = note
                            break
                    # Check if main concept found
                    if not main_concept:
                        pass # TODO: ask GPT to return the main concept
                    # Generate Concept Database
                    self.concept_database = ConceptDatabase(main_concept, self.env.notebank.env_string(),)
                    # Generate Slide Planner
                    # TODO: Generate Slide Planner
                    
                    # Generate Question Suite:
                    # TODO: Generate question suite
                    
                    # Transition
                    self.env.current_state = int(TutorEnv.States.TEACHING)
                return prompt_obj.format_json() # TODO: fix for 
            
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
        self.current_state = int(TutorEnv.States.PROMPTING) # Prompt Start
        self.notebank = NoteBank()
        self.chat_history = ChatHistory()
        self.prompter = Prompter("AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/question_prompt", "AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/notebank_prompt", "AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/prompt_plan_prompt", self.notebank, self.chat_history)
        self.concept_database = None
        self._has_concept_database = False
        self.executor = TutorEnv.Executor(self,)
        self.States = [
                None,# Prompting States TODO: Change to be a Ptr to Prompter 
                None, # Teaching States
                None, # Guiding States
                None  # Testing States
            ]
    
    def step(self, input_data):
        return self.executor.process_action(input_data), self.current_state
        
    
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
        
            