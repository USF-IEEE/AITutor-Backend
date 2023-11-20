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
USE_OPENAI = True

class QuestionSuite:
    ALLOWED_LIBS = [
        ["numpy", "math", "sympy", ], # Math
        ["numpy", "math", "sympy", "collections", "itertools", "re", "heapq", "functools", "string", "torch", "nltk", "PIL", "cv2", "json", "enum", "typing",], # Python Programming
        None,
        None
        ]
    
    def __init__(self, ConceptDatabase):
        
        self.__ConceptDatabase = ConceptDatabase

class QuestionPlanner:
    class QuestionLLMAPI:
        CURR_ENV_NOTEBANK_DELIMITER = "$NOTEBANK.STATE$" #Environment for the notebankd
        CURR_ENV_CHAT_HISTORY_DELIMITER = "$CHAT_HISTORY$" #Environment for the chat history
        PLAN_DELIMITER = "$QUESTION_PLAN$"
        CURR_ERROR_DELIMITER = "$CURR_ENV.ERROR$"

        def __init__(self, ):
            self.client = openai.OpenAI() if USE_OPENAI else ReplicateAPI()
        
        def request_output_from_llm(self, prompt, model: str):
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
                    max_tokens=3000,
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

    
class Question:
    __QUESTION_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    
    def Subject(IntEnum):
        MATH=0 # Requires latex_code
        CODE=1 # Requires test_cases
        LITERATURE=2 # Requires passage
        CONCEPTUAL=3 # 
        
    def Type(IntEnum):
        TEXT_ENTRY=0 # Requires Rubric
        MULTIPLE_CHOICE=1 # Requires Correct Answer
        CALCULATION_ENTRY=2 # Requires calculation_script 
        CODE_ENTRY=3 # Requires Code Executor
    
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
         self.concepts = concepts
         self.student_response = None # Initialize to None
         
         
    def __repr__(self) -> str:
        return f"Concept(name: {self.name}) <{self.__hash__()}>"

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

        q_subject = question_data.get('subject', None)
        q_type = question_data.get('type', None)
        q_concepts = question_data.get("concepts", None)
        q_data = question_data.get("data", None)
        assert q_subject, f"Error while determining Question's subject field, ensure your output for parameter \"subject\" was of type int and also included in your output. Ouput: {llm_output}"
        assert q_type, f"Error while determining Question's type field, ensure your output for parameter \"type\" was of type int and also included in your output. Ouput: {llm_output}"
        assert q_concepts, f"Error while determining Question's concepts field, ensure your output for parameter \"concepts\" was of type list[str] and also included in your output. Ouput: {llm_output}"
        assert q_data, f"Error while determining Question's data field, ensure your output for parameter \"data\" was of type str and also included in your output. Ouput: {llm_output}"
        try:
            q_subject = Question.Subject(q_subject)
        except ValueError:
            raise Exception(f"Error while determining Question's Subject, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        try:
            q_type = Question.Type(q_type)
        except ValueError:
            raise Exception(f"Error while determining Question's Type, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        try:
            q_concepts = [concept for concept in map(concepts, ConceptDatabase.get_concept) if concept is not None]
        except:
            raise Exception(f"Error while determining Question's Concept Mappings, ensure your output for parameter \"concepts\" was of type List[str] and the concepts exist in the database. Ouput: {llm_output}")
        
        q_data = {k:v for k, v in question_data.items() if k not in ('subject', 'type')}
        
        # Type Based Assertions
        if q_type == Question.Type.MULTIPLE_CHOICE:
            assert len([k for k in q_data.keys() if "entry" in k]) > 1, f"Error in creating Multiple Choice Question: provided less than 2 Choices. Output: {llm_output}"
            assert q_data.get("correct_entry", None), "Error in creating Multiple Choice Question: did not provide correct_entry field (the correct answer choice)"
            
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
        
        elif q_type == Question.Suject.MATH:
            assert "latex_code" in q_data, f"Error in creating Math Question: \"calculation_script\" parameter for computing the value of the question is missing. Output: {llm_output}"
            
        # Code Questions taken care of by code entry
        # Conceptual Questions do not require any additional checks, as they are topic related questions that are either open-ended or multiple choice. The TEXT ENTRY checks and the MULTIPLE_CHOICE checks already assure this to be the case.
        
    
    def evaluate_user_input(self, user_input):
        """Based on the user_input, evaluate the question and return a value between [0-5].

        Args:
            user_input (str): 
        """
        pass 
        
    
    def to_sql(self,) -> Tuple[str, str, str]:
        """Returns the state of Concept

        Returns:
            Tuple[str, str, str]: (concept_name, concept_def, concept_latex) 
        """