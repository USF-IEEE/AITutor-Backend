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
        MATH=0
        CODE=1
        LITERATURE=2
        CONCEPTUAL=3
        
    def Type(IntEnum):
        TEXT_ENTRY=0 # Requires Rubric
        MULTIPLE_CHOICE=1 # Requires Correct Answer
        MATH_ENTRY=2 # Requires Calculator 
        CODE_ENTRY=3 # Requires Code Executor
    
    def __init__(self, q_subject: 'Question.Subject', q_type: 'Question.Type', question_data:dict, concepts):
         """
            Defined Data Fields
            
            - Math:
              - question_data "str"
              - latex_code "render code for question (str)"
              - entry_1 (Multiple Choice)
              - entry_2 (Multiple Choice)
              ...
              
            - Code:
              - question_data "str"
              - test_cases "str" # Assert Final print is True
              
            - Literature:
              - question_data (about a passage of text)
              - reading_passage "str"
              - rubric "(str) Grading rubric"
              - entry_1 # if multiple choice
              - entry_2
              ...
            
            - Conceptual:
              - Question
              - rubric "(str) Grading rubric"
              - entry_1 # if multiple choice
              - entry_2
              ...
              
            
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

        q_subject = question_data['subject']
        q_type = question_data['type']
        try:
            q_subject = Question.Subject(q_subject)
        except ValueError:
            raise Exception(f"Error while determining Question's Subject, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        try:
            q_type = Question.Type(q_type)
        except ValueError:
            raise Exception(f"Error while determining Question's Type, ensure your input was of type int and is a proper enum value. Ouput: {llm_output}")
        
        q_data = {k:v for k, v in question_data.items() if k not in ('subject', 'type')}
        if q_type == Question.Type.MULTIPLE_CHOICE:
            assert len([k for k in q_data.keys() if "entry" in k]) > 1, f"Error in creating Multiple Choice Question: provided less than 2 Choices. Output: {llm_output}"
        
        
        concepts = concepts
        student_response = None
        

        
    
    def to_sql(self,) -> Tuple[str, str, str]:
        """Returns the state of Concept

        Returns:
            Tuple[str, str, str]: (concept_name, concept_def, concept_latex) 
        """
        
    