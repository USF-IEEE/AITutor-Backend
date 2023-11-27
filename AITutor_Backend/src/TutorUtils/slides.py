import json
from typing import List, Tuple, Union
import re
from enum import IntEnum
import openai
from AITutor_Backend.src.BackendUtils.json_serialize import *
from AITutor_Backend.src.BackendUtils.json_serialize import JSONSerializable
from AITutor_Backend.src.TutorUtils.concepts import *

from enum import IntEnum
from typing import List, Tuple

class Purpose(IntEnum):
    Introductory = 0
    Relative = 1
    Exploratory = 2
    Explanative = 3
    Examplative = 4

class Slide(JSONSerializable):
    def __init__(self, title: str, paragraph: str, latex_codes: List[Tuple[str, str]], purpose: Purpose, purpose_statement: str, concepts: List[Concept]):
        self.title = title
        self.paragraph = paragraph
        self.latex_codes = latex_codes
        self.purpose = purpose
        self.purpose_statement = purpose_statement
        self.concepts = concepts

    def format_json(self):
        return {
            "title": self.title,
            "paragraph": self.paragraph,
            "latex_codes": self.latex_codes,
            "purpose": self.purpose.name,
            "purpose_statement": self.purpose_statement,
            "concepts": [concept.name for concept in self.concepts]
        }

class SlidePlan(JSONSerializable):
    __SLIDEPLAN_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    def __init__(self, title: str, purpose: Purpose, purpose_statement: str, concepts: List[Concept]):
        self.title = title
        self.purpose = purpose
        self.purpose_statement = purpose_statement
        self.concepts = concepts

    def format_json(self):
        return {
            "title": self.title,
            "purpose": self.purpose.name,
            "purpose_statement": self.purpose_statement,
            "concepts": [concept.name for concept in self.concepts]
        }
    @staticmethod
    def create_slideplan_from_JSON(llm_output, ConceptDatabase):
        regex_match = SlidePlan.__SLIDEPLAN_REGEX.findall(llm_output)
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        slideplan_data = regex_match if regex_match else llm_output
        try:
            slideplan_data = json.loads(slideplan_data)
        except json.JSONDecodeError:
            raise ValueError(f"Error parsing JSON on output: {llm_output},  Ensure your response was in JSON Format")
        # Validating the title
        title = slideplan_data.get('title')
        assert title and type(title) == str, "Invalid or missing title in SlidePlan JSON data"

        # Validating the purpose
        purpose = int(slideplan_data.get('purpose', -1))
        assert isinstance(purpose, Purpose), "Purpose did not map correctly, ensure you have provided a valid ENUM Value."

        # Validating the purpose statement
        purpose_statement = slideplan_data.get('purpose_statement')
        assert purpose_statement and type(purpose_statement) == str, "Invalid or missing purpose statement in SlidePlan JSON data"

        # Validating the concepts
        concept_names = slideplan_data.get('concepts')
        assert concept_names and type(concept_names) == list, "Invalid or missing concepts in SlidePlan JSON data"
        
        concepts = [ConceptDatabase.get_concept(name) for name in concept_names]
        assert concepts, "One or more concepts are not recognized in SlidePlan JSON data"

        return SlidePlan(title, purpose, purpose_statement, concepts)

class SlidePlanner:
    class SlideLLMAPI:
        SLIDE_PLAN_SET_DELIMITER = "$ENV.SLIDE_PLAN_SET$" #Environment for the notebankd
        EXPLORED_CONCEPTS_DELIMITER = "$ENV.CONCEPTS_EXPLORED_VALUES$" #Environment for the chat history
        NOTEBANK_STATE_DELIMITER = "$ENV.NOTEBANK_STATE$"
        CURR_ENV_CONEPT_LIST = "$ENV.CONCEPT_LIST$"

        def __init__(self, slideplan_plan_prompt_file, slideplan_plan_to_obj_prompt_file, ):
            self.client = openai.OpenAI() if USE_OPENAI else ReplicateAPI()
            with open(slideplan_plan_prompt_file, "r") as f:
                self.__slideplan_plan_prompt = f.read()
            with open(slideplan_plan_to_obj_prompt_file, "r") as f:
                self.__slideplan_plan_to_obj_prompt = f.read()
                
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
        
        def prompt_plan_slideplan(self, side_plan_set, explored_concepts, notebank_state):
            env_state = {SlidePlanner.SlideLLMAPI.SLIDE_PLAN_SET_DELIMITER: side_plan_set, SlidePlanner.SlideLLMAPI.EXPLORED_CONCEPTS_DELIMITER: explored_concepts, SlidePlanner.SlideLLMAPI.NOTEBANK_STATE_DELIMITER:notebank_state}
            return self._load_prompt(self.__slideplan_plan_prompt, env_state)
    
        def prompt_sideplan_to_obj(self, slide_plan):
            env_state = {"$SLIDE_PLAN$": slide_plan}
            return self._load_prompt(self.__slideplan_plan_to_obj_prompt, env_state)
        
    def __init__(self, Notebank, ConceptDatabase):
        self.SlidePlans = []
        self.Slides = []
        self.Notebank = Notebank
        self.ConceptDatabase = ConceptDatabase
        self.num_slides = 0
        self.current_obj_idx = 0
        self.llm_api = SlidePlanner.SlideLLMAPI() # LLM API for generating slide plans

    def generate_slide_plan(self):
        notebank_state = self.Notebank.env_str()
        while True:
            # Prepare input for LLM
            current_slideplans_str = self._generate_slideplans_str()
            concept_exploration_map_str = self._generate_concept_exploration_map_str()
            prompt = self._build_llm_prompt(current_slideplans_str, concept_exploration_map_str)
            slideplan_prompt = self.llm_api.prompt_plan_slideplan(self._generate_slideplans_str(), self._generate_concept_exploration_map_str())
            # Request output from LLM
            llm_output = self.llm_api.request_output_from_llm(slideplan_prompt, "gpt-4")    
            if "[TERM]" in llm_output:
                break
            
            # Convert:
            conversion_prompt = self.llm_api.prompt_sideplan_to_obj(llm_output)
            for i in range(5):
                try:
                    llm_output = self.llm_api.request_output_from_llm(conversion_prompt, model="gpt-3.5-turbo-16k")    
                    slide_plan = SlidePlan.create_slideplan_from_JSON(llm_output)
                except: # TODO: Fix error handling
                    pass
                if slide_plan: break
            self.SlidePlans.append(slide_plan)

    def _generate_slideplans_str(self):
        return '\n'.join([f"{slide_plan.title}: {slide_plan.purpose.name}, {slide_plan.purpose_statement}, Concepts: {', '.join([c.name for c in slide_plan.concepts])}" for slide_plan in self.SlidePlans])

    def _generate_concept_exploration_map_str(self):
        return '\n'.join([f"{concept.name}: {sum([1 for slide_plan in self.SlidePlans if concept in slide_plan.concepts])}" for concept in self.ConceptDatabase.get_concepts()])
    