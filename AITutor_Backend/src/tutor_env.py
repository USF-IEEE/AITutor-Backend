from enum import IntEnum
from collections import deque
from AITutor_Backend.src.TutorUtils.notebank import *
from AITutor_Backend.src.TutorUtils.chat_history import *
from AITutor_Backend.src.BackendUtils.sql_serialize import *
from AITutor_Backend.src.TutorUtils.prompts import Prompter, PromptAction
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase
from AITutor_Backend.src.TutorUtils.slides import SlidePlanner, Slide
from AITutor_Backend.src.TutorUtils.questions import QuestionSuite
from AITutor_Backend.src.BackendUtils.replicate_api import ReplicateAPI
from concurrent.futures import ThreadPoolExecutor

class TutorEnv(SQLSerializable,):
    class States(IntEnum):
            PROMPTING=0
            TEACHING=1
            GUIDING=2
            TESTING=3
            GENERATION=4
    class Executor(SQLSerializable,):
        def __init__(self, env:'TutorEnv', main_concept_file, concept_list_file, notebank_filter_file):
            super(TutorEnv.Executor, self).__init__()
            self.env = env
            self.__ears = None # TODO: Add whisper-3 api
            self.__mouth = None # TODO: Add 
            self.__brain = None # TODO: Add LLM API Reference
            with open(main_concept_file, "r") as f:
                self.__main_concept_prompt = f.read()
            with open(concept_list_file, "r") as f:
                self.__concept_list_prompt = f.read()
            with open(notebank_filter_file, "r") as f:
                self.__notebank_filter_prompt = f.read()
        
        def slide_planner_task(self):
            try:
                self.env.slide_planner.generate_slide_plan()
                self.env.slide_planner.generate_slide_deque()
            except Exception as e:
                print(f"Error while creating Slide Planner: {e}")
                return False
            return True

        def question_suite_task(self,):
            try:
                self.env.question_suite.generate_question_data()
            except Exception as e:
                print("Error while creating Question Suite: {e}")
                return False
            return True

        def __get_main_concept(self, ):
            import openai
            client = openai.Client()
            while True:
                f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
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
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {
                            "role": "system",
                            "content": self.__concept_list_prompt,
                        },
                        {
                            "role": "system",
                            "content": f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:",
                        }
                    ],
                    # response_format={"type": "json_object"},
                    temperature=1.0,
                    max_tokens=1256,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                try:
                    json_regex = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
                    regex_match = json_regex.findall(response.choices[0].message.content)
                    assert regex_match
                    regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
                    json_data = json.loads(regex_match)
                    if "concept_list" in json_data: return json_data["concept_list"]
                except:
                    pass

        def __get_filtered_notebank(self,):
            import openai
            client = openai.Client()
            while True:
                f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {
                            "role": "system",
                            "content": self.__notebank_filter_prompt,
                        },
                        {
                            "role": "system",
                            "content": f"// Input:\n {self.env.notebank.env_string()}\n\n// Output:",
                        }
                    ],
                    # response_format={"type": "json_object"},
                    temperature=1.0,
                    max_tokens=8000,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                try:
                    notes = (response.choices[0].message.content).split("\n")
                    if len(notes) > 3: return notes
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
                if terminate or prompt_obj._type == PromptAction.Type.TERMINATE:
                    print(self.env.notebank.env_string())
                    concept_list = self.__get_concept_list()
                    print(concept_list)
                    self.env.current_state = int(TutorEnv.States.GENERATION)
                    # TODO: Implement generation 
                    prompt_obj = PromptAction("[SEP]".join(concept_list),
                                              PromptAction.Type.TERMINATE, []) # fix to return teaching objects
                return prompt_obj.format_json()
            ### END PROMPTING PHASE
            
            ### GENERATION PHASE
            if self.env.current_state == TutorEnv.States.GENERATION:
                 # Generate Concept Database
                    # Add new concepts:
                    for concept in user_input["list_concepts"]:
                        self.env.notebank.add_note(f"Concept: {concept}")
                    self.env.notebank.add_note(f"Student's Interest Statement: {user_input['student_interests']}")
                    self.env.notebank.add_note(f"Student's Slides Preference Statement: {user_input['student_slides']}")
                    self.env.notebank.add_note(f"Student's Questions Preference Statement: {user_input['student_questions']}")
                    main_concept = self.__get_main_concept()
                    self.env.notebank.add_note(f"Main Concept: {main_concept}")

                    # Filter Notebank:
                    notes = self.__get_filtered_notebank()
                    self.env.notebank.clear()
                    [self.env.notebank.add_note(note) for note in notes] # iterate through notes and add to Notebank
                    # Generate Concept Database:
                    self.env.concept_database = ConceptDatabase(main_concept, self.env.notebank.env_string(),)
                    # # Generate Slide Planner:
                    self.env.slide_planner = SlidePlanner(self.env.notebank, self.env.concept_database)
                    # # Generate Question Suite:
                    num_questions = int(user_input["num_questions"])
                    self.env.question_suite = QuestionSuite(num_questions, self.env.notebank, self.env.concept_database)
                    self.env.current_state = TutorEnv.States.TEACHING
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        # Submit slide planner tasks
                        slide_planner_future = executor.submit(self.slide_planner_task)
                        # Submit question suite task
                        question_suite_future = executor.submit(self.question_suite_task, num_questions)
                        # Wait for the slide planner task to complete
                        slide_planner_result = slide_planner_future.result()
                        # Wait for the question suite task to complete
                        question_suite_result = question_suite_future.result()
                        assert slide_planner_result and question_suite_result, "Failed at creating Question Suite or Slide Planner. Check for error in logs."

                    learning_obj = self.env.slide_planner.format_json()
                    
                    return learning_obj
            ### END GENERATION PHASE

            self.env.current_state = int(user_input["current_state"])

            ### TEACHING PHASE
            if self.env.current_state == int(TutorEnv.States.TEACHING):
                obj_idx = user_input.get("obj_idx", self.slide_planner.current_obj_idx)
                if obj_idx == self.slide_planner.current_obj_idx:
                    # TODO: listen to user user_input and create a response 
                    self.env.chat_history.hear(user_prompt)
                    # ...
                    return self.env.slide_planner.format_json().update({"tutor_statement": "todo: implement"})
                else:
                    return self.env.slide_planner.format_json().update({"tutor_statement": self.env.slide_planner.get_object(obj_idx).presentation})
            ### END TEACHING PHASE
            
            ### TESTING PHASE
            if self.env.current_state == int(TutorEnv.States.TESTING):
                obj_idx = user_input.get("obj_idx", self.slide_planner.current_obj_idx)
                if obj_idx == self.slide_planner.current_obj_idx:
                    if user_input["eval_response"]:
                        # TODO: Evaluate the response the the question
                        return self.env.question_suite.format_json().update({"tutor_statement": "todo: implement"})
                    else:
                        # TODO: listen to user user_input and create a response 
                        self.env.chat_history.hear(user_prompt)
                    # ...
                    return self.env.question_suite.format_json().update({"tutor_statement": "todo: implement"})
                else:
                    return self.env.question_suite.format_json().update({"tutor_statement": self.env.question_suite.get_object(obj_idx).presentation})
            ### END TESTING PHASE

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
        self.slide_planner = None
        self.question_suite = None
        self._content_generated = False
        self.executor = TutorEnv.Executor(self, "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/main_concept_prompt", "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/concept_list_prompt", "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/notebank_filter_prompt")
    
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
        tutor_ref.prompter.notebank = tutor_ref.notebank
        tutor_ref.prompter.chat_history = tutor_ref.chat_history
        return tutor_ref
            
    def to_sql(self,) -> str:
        """Serializes a Chat History for SQL

        Returns:
            str: Chat History
        """
        return self.current_state
        
            