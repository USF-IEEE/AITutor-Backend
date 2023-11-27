from enum import IntEnum
from typing import Tuple, List
import re
import yaml
import os
import openai
import json

from AITutor_Backend.src.BackendUtils.replicate_api import ReplicateAPI
from AITutor_Backend.src.BackendUtils.code_executor import CodeExecutor
from AITutor_Backend.src.DataUtils.nlp_utils import edit_distance
from AITutor_Backend.src.BackendUtils.sql_serialize import SQLSerializable
from AITutor_Backend.src.BackendUtils.json_serialize import JSONSerializable
USE_OPENAI = True

class QuestionSuite(JSONSerializable, SQLSerializable):
    ALLOWED_LIBS = [
        ["numpy", "math", "sympy", ], # Math
        ["numpy", "math", "sympy", "collections", "itertools", "re", "heapq", "functools", "string", "torch", "nltk", "PIL", "cv2", "json", "enum", "typing",], # Python Programming
        None,
        None
        ]
    class QuestionLLMAPI:
        CURR_ENV_NOTEBANK_DELIMITER = "$ENV.NOTEBANK_STATE$" #Environment for the notebankd
        CURR_ENV_QS_CREATED_DELIMITER = "$ENV.QUESTIONS_CREATED_SUMMARY$" #Environment for the chat history
        CURR_ENV_MAIN_CONCEPT = "$ENV.MAIN_CONCEPT$"
        CURR_ENV_CONEPT_LIST = "$ENV.CONCEPT_LIST$"
        QUESTION_PLAN_DELIMITER = "$ENV.QUESTION_PLAN$"
        CURR_ERROR_DELIMITER = "$ENV.CURR_ERROR$"

        def __init__(self,question_plan_prompt_file, question_plan_to_question_file, ):
            self.client = openai.OpenAI() if USE_OPENAI else ReplicateAPI()
            with open(question_plan_prompt_file, "r") as f:
                self.__question_plan_prompt = f.read()
            with open(question_plan_to_question_file, "r") as f:
                self.__plan_to_question_prompt = f.read()
                
        def request_output_from_llm(self, prompt, model: str, max_length = 4000):
            """Requests the Concept information from an LLM.

            Args:
                prompt: (str) - string to get passed to the model
                model: (str) - 

            Returns:
                _type_: _description_
            """
            if USE_OPENAI:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": prompt,
                        },
                    ],
                    temperature=1,
                    max_tokens=max_length,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )

                return response.choices[0].message.content
            else:
                return self.client.get_output(prompt, " ")
            
        def _load_prompt(self, prompt_template, state_dict):
            prompt_string = prompt_template
            # Replace Values in Prompt:
            for k, v in state_dict.items():
                prompt_string = prompt_string.replace(k, v)

            # Return Prompt:
            return prompt_string
        
        def prompt_plan_question(self, main_concept, concept_list, questions_created, notebank_state, curr_error):
            env_state = {QuestionSuite.QuestionLLMAPI.CURR_ENV_MAIN_CONCEPT: main_concept, QuestionSuite.QuestionLLMAPI.CURR_ENV_CONEPT_LIST: concept_list, QuestionSuite.QuestionLLMAPI.CURR_ENV_QS_CREATED_DELIMITER: questions_created, QuestionSuite.QuestionLLMAPI.CURR_ENV_NOTEBANK_DELIMITER:notebank_state, QuestionSuite.QuestionLLMAPI.CURR_ERROR_DELIMITER:curr_error}
            return self._load_prompt(self.__question_plan_prompt, env_state)
    
        def plan_to_question(self, main_concept, concept_list, q_plan, curr_error):
            env_state = {QuestionSuite.QuestionLLMAPI.CURR_ENV_MAIN_CONCEPT: main_concept, QuestionSuite.QuestionLLMAPI.CURR_ENV_CONEPT_LIST: concept_list, QuestionSuite.QuestionLLMAPI.QUESTION_PLAN_DELIMITER: q_plan, QuestionSuite.QuestionLLMAPI.CURR_ERROR_DELIMITER:curr_error}
            return self._load_prompt(self.__plan_to_question_prompt, env_state)
        
    def __init__(self, num_questions, Notebank, ConceptDatabase):
        self.current_obj_idx = -1
        self.__Notebank = Notebank
        self.__ConceptDatabase = ConceptDatabase
        assert isinstance(num_questions, int), "Cannot Create a QuestionSuite without specifying (int) number of questions. Check the Data Type provided for num_questions"
        self.num_questions = max(min(25, num_questions), 5)
        self.Questions = []
        self.llm_api = QuestionSuite.QuestionLLMAPI("AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/plan_question_prompt", "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/plan_to_question_prompt", )
        
    def generate_question_data(self, ):
        concept_list_str = self.__ConceptDatabase.get_concept_list_str()
        notebank_str = self.__Notebank.env_string()
        # Iterate through the Questions and Generate
        for question_idx in range(self.num_questions):
            current_questions = self.env_string()
            error = "There is no current error."
            while True:
                try: # Build Question Plan:
                    prompt = self.llm_api.prompt_plan_question( self.__ConceptDatabase.main_concept, concept_list_str, current_questions, notebank_str, error )
                    q_plan = self.llm_api.request_output_from_llm(prompt, "gpt-4-1106-preview", max_length = 3000)
                    break
                except Exception as e:
                    error = f"Error while creating a Question Plan: {e}"
            error = "There is no current error."
            while True:
                try:
                    prompt = self.llm_api.plan_to_question( self.__ConceptDatabase.main_concept, concept_list_str, q_plan, error)
                    llm_output = self.llm_api.request_output_from_llm(prompt, "gpt-3.5-turbo-16k", max_length=5000)
                    question = Question.create_question_from_JSON(llm_output, self.__ConceptDatabase)
                    assert question, f"Error while creating Question, check the input: {llm_output}"
                    assert isinstance(question.type, Question.Type), f"Error, could not find type on question, check the input: {llm_output}"
                    assert isinstance(question.subject, Question.Subject), f"Error, could not find subject on question, check the input: {llm_output}"
                    assert question.concepts, f"Error, could not find Concept Database Mappings on Question JSON object. Check the output to ensure that these were included: {llm_output}"
                    break
                except Exception as e:
                    error = f"Error while converting a Question Plan into a Question JSON Object: {e}"

            self.Questions.append(question)
        self.current_obj_idx = 0
            
    def env_string(self,):
        map_question = lambda x: f'{x.subject}, {x.type}, Concepts: {", ".join([concept.name for concept in x.concepts])}'
        return '\n'.join([f"{str(i)}: " + map_question(question) for i, question in enumerate(self.Questions)]) if self.Questions else "// There are no Questions created currently."

    def to_sql(self):
        """Concert QuestionSuite into SQL Database
        returns:
            - Tuple[int, int, List[Questions]] (Current Obj Idx, num_questions, Questions)
        """
        return (self.current_obj_idx, self.num_questions, [question.to_sql() for question in self.Questions])
    
    def from_sql(current_obj_idx, num_questions, questions:List[Tuple[int, int, str, List[str]]], Notebank, ConceptDatabase):
        q_suite = QuestionSuite(num_questions, Notebank, ConceptDatabase)
        q_suite.current_obj_idx = current_obj_idx
        q_suite.Questions = [Question.from_sql(q[0], q[1], q[2], [ConceptDatabase.get_concept(cpt) for cpt in q[3]]) for q in questions]
        return q_suite
        
class Question(JSONSerializable, SQLSerializable):
    __QUESTION_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    class Subject(IntEnum):
        MATH=0 # Requires latex_code
        CODE=1 # Requires test_cases
        LITERATURE=2 # Requires passage
        CONCEPTUAL=3 # 
        
    class Type(IntEnum):
        TEXT_ENTRY=0 # Requires Rubric
        MULTIPLE_CHOICE=1 # Requires Correct Answer
        CALCULATION_ENTRY=2 # Requires calculation_script 
        CODE_ENTRY=3 # Requires Code Executor
    MAP_SUBJECT_2_STR = {0: "Math (0)", 1: "Code (1)" , 2: "Literature (2)", 3: "Conceptual (3)"}
    MAP_TYPE_2_STR = {0: "TEXT_ENTRY (0)",1: "MULTIPLE_CHOICE (1)", 2:"CALCULATION_ENTRY (2)", 3:"CODE_ENTRY (3)"}
    def __init__(self, q_subject: 'Question.Subject', q_type: 'Question.Type', question_data:dict, concepts):
         """
            Defined Data Fields
            
            - Math:
              - data "str" (about a math question)
              - latex_code "render code for question (str)"
              - entry_1 (Multiple Choice) # if multiple choice
              - entry_2 (Multiple Choice)
              ...
              
            - Code:
              - data "str" (about a coding question)
              - test_cases "str" # Assert Final print is True
              
            - Literature:
              - data (about a passage of text)
              - reading_passage "str"
              - rubric "(str) Grading rubric" # if TEXT_ENTRY
              - entry_1 # if multiple choice
              - entry_2
              ...
              - correct_entry # if multiple choice
            
            - Conceptual:
              - Question
              - rubric "(str) Grading rubric" # if TEXT_ENTRY
              - entry_1 # if multiple choice
              - entry_2
              ...
              - correct_entry # if multiple choice
            
         """
         self.subject = q_subject
         self.type = q_type
         self.data = question_data
         self.concepts = [c for c in concepts if c is not None]
         self.student_response = None # Initialize to None
         
    def __repr__(self) -> str:
        return f"Question(data: {self.data}) <{self.__hash__()}>"

    @staticmethod
    def create_question_from_JSON(llm_output, ConceptDatabase) -> 'Question':
        """

        """
        regex_match = Question.__QUESTION_REGEX.findall(llm_output)
        # Try to get json format or attempt to use output as json
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        question_data = regex_match if regex_match else llm_output
        try:
            question_data = json.loads(question_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON on output: {llm_output},  error: {str(e)}")

        q_subject = question_data.get('subject', -1)
        q_type = question_data.get('type', -1)
        q_concepts = question_data.get("concepts", None)
        q_data = question_data.get("data", None)
        assert q_subject != -1, f"Error while determining Question's subject field, ensure your output for parameter \"subject\" was of type int and also included in your output. Ouput: {llm_output}"
        assert q_type != -1, f"Error while determining Question's type field, ensure your output for parameter \"type\" was of type int and also included in your output. Ouput: {llm_output}"
        assert q_concepts, f"Error while determining Question's concepts field, ensure your output for parameter \"concepts\" was of type list[str] and also included in your output. Ouput: {llm_output}"
        assert q_data, f"Error while determining Question's data field, ensure your output for parameter \"data\" was of type str and also included in your output. Ouput: {llm_output}"
        assert q_data, "Did not include question data in JSON object."
        try:
            q_subject = Question.Subject(q_subject)
        except ValueError:
            raise Exception(f"Error while determining Question's Subject, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        try:
            q_type = Question.Type(q_type)
        except ValueError:
            raise Exception(f"Error while determining Question's Type, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        try:
            q_concepts = [concept for concept in map(ConceptDatabase.get_concept, q_concepts) if concept is not None]
        except:
            raise Exception(f"Error while determining Question's Concept Mappings, ensure your output for parameter \"concepts\" was of type List[str] and the concepts exist in the database. Ouput: {llm_output}")
        
        q_data = {k:v for k, v in question_data.items() if k not in ('subject', 'type')}
        
        # Type Based Assertions
        if q_type == Question.Type.MULTIPLE_CHOICE:
            assert len([k for k in q_data.keys() if "entry" in k and not "correct" in k]) > 1, f"Error in creating Multiple Choice Question: provided less than 2 Choices. Output: {llm_output}"
            assert q_data.get("correct_entry", None) and q_data["correct_entry"] in q_data and "entry" in q_data["correct_entry"], "Error in creating Multiple Choice Question: did not provide correct_entry field (the correct answer choice)"
            
        elif q_type == Question.Type.TEXT_ENTRY:
            assert "rubric" in q_data, "Error in creating Text Entry Question: Rubric is required."

        elif q_type == Question.Type.CALCULATION_ENTRY:
            assert "calculation_script" in q_data, f"Error in creating Math Entry Question: calculation_script for computing the value of the question is missing. Output: {llm_output}"

        elif q_type == Question.Type.CODE_ENTRY:
            assert "test_cases_script" in q_data, f"Error in creating Code Entry Question: Test cases script was not provided. Output: {llm_output}"
            # Note: Code Executor is a parameter attached to the program regardless. 
        
        ### Subject Based Assertions
        if q_subject == Question.Subject.LITERATURE:
           assert "reading_passage" in q_data, f"Error in creating Literature Question: \"reading_passage\" parameter was not provided. Output: {llm_output}"
        
        elif q_subject == Question.Subject.MATH:
            assert "latex_code" in q_data, f"Error in creating Math Question: \"latex_code\" parameter for displaying the equation is missing. Output: {llm_output}"
            
        # Code Questions taken care of by code entry
        # Conceptual Questions do not require any additional checks, as they are topic related questions that are either open-ended or multiple choice. The TEXT ENTRY checks and the MULTIPLE_CHOICE checks already assure this to be the case.
        
        return Question(q_subject, q_type, q_data, q_concepts)
    
    def evaluate_user_input(self, user_input):
        """Based on the user_input, evaluate the question and return a value between [0-5].

        Args:
            user_input (str): 
        """
        pass 
        
    
    def to_sql(self,) -> Tuple[str, str, str]:
        """Returns the state of Concept

        Returns:
            Tuple[str, str, str, List[str]]: (self.subject, self.type, self.data, self.concepts) 
        """
        return (int(self.subject), int(self.type), json.dumps(self.data), [c.name for c in self.concepts])
    
    def format_json(self, ):
        """convert question into JSON object

        Returns:
            _type_: _description_
        """
        return { \
                "subject": int(self.subject), \
                "type": int(self.type), \
                "data": self.data.copy() \
            }
    
    @staticmethod
    def from_sql(q_subject:int, q_type:int, q_data:str, concepts,) -> 'Question':
        """Returns the state of Concept
            - Tuple[str, str, str]: (self.subject, self.type, self.data) 

        Returns:
            - Question: representing the class
        """
        return Question(Question.Subject(q_subject), Question.Type(q_type), dict(json.loads(q_data)), concepts)