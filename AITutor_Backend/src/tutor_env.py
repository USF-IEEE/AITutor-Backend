from enum import IntEnum
from collections import deque
from AITutor_Backend.src.TutorUtils.notebank import *
from AITutor_Backend.src.TutorUtils.chat_history import *
from AITutor_Backend.src.BackendUtils.sql_serialize import *
from AITutor_Backend.src.TutorUtils.prompts import Prompter, PromptAction
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase
from AITutor_Backend.src.TutorUtils.questions import QuestionSuite
from AITutor_Backend.src.BackendUtils.replicate_api import ReplicateAPI

class TutorEnv(SQLSerializable,):
    class States(IntEnum):
            PROMPTING=0
            TEACHING=1
            GUIDING=2
            TESTING=3
            GENERATION=4
    class Executor(SQLSerializable,):
        def __init__(self, env:'TutorEnv', main_concept_file):
            super(TutorEnv.Executor, self).__init__()
            self.env = env
            self.__ears = None # TODO: Add whisper-3 api
            self.__mouth = None # TODO: Add 
            self.__brain = None # TODO: Add LLM API Reference
            with open(main_concept_file, "r") as f:
                self.__main_concept_prompt = f.read()
            
        def __get_main_concept(self, ):
            import openai
            client = openai.Client()
            while True:
                f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": self.__main_concept_prompt,
                        },
                        {
                            "role": "system",
                            "content": f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:",
                        }
                    ],
                    # response_format={"type": "json_object"},
                    temperature=0.8,
                    max_tokens=256,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                try:
                    json_data = json.loads(response.choices[0].message.content)
                    if "main_concept" in json_data: return json_data["main_concept"]
                except:
                    pass
                
        def __get_concept_list(self,):
            import openai
            client = openai.Client()
            while True:
                f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": self.__main_concept_prompt,
                        },
                        {
                            "role": "system",
                            "content": f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:",
                        }
                    ],
                    # response_format={"type": "json_object"},
                    temperature=1.0,
                    max_tokens=256,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                try:
                    json_data = json.loads(response.choices[0].message.content)
                    if "concept_list" in json_data: return json_data["concept_list"]
                except:
                    pass
                
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
            
            ### PROMPTING PHASE
            if self.env.current_state == int(TutorEnv.States.PROMPTING):
                prompt_obj, terminate = self.env.prompter.perform_tutor(user_prompt)
                if terminate:
                    concept_list = self.__get_concept_list()
                    self.env.current_state = int(TutorEnv.States.GENERATION)
                    # TODO: Implement generation 
                    prompt_obj = PromptAction("[SEP]".join(concept_list),
                                              PromptAction.Type.TERMINATE) # fix to return teaching objects
                return prompt_obj.format_json()
            ### END PROMPTING PHASE
            
            if self.env.current_state == TutorEnv.States.GENERATION:
                 # Generate Concept Database
                    # Add new concepts:
                    for concept in user_input["list_concepts"]:
                        self.env.notebank.add_note(f"Concept: {concept}")
                    main_concept = self.__get_main_concept()
                    self.env.notebank.add_note(f"Main Concept: {main_concept}")
                    self.concept_database = ConceptDatabase(main_concept, self.env.notebank.env_string(),)
                    # # Generate Slide Planner
                    # # TODO: Generate Slide Planner
                    
                    # # Generate Question Suite:
                    # # TODO: Generate question suite
                    num_questions = int(user_input["num_questions"])
                    self.question_suite = QuestionSuite(num_questions, self.env.notebank, self.env.concept_database)
                    # Transition
                    
                    self.env.current_state = TutorEnv.States.TEACHING
                    return {"test": "done generating"}
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
        self.question_suite = None
        self._content_generated = False
        self.executor = TutorEnv.Executor(self, "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/main_concept_prompt")
    
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
        
            