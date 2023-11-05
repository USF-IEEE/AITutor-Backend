from typing import Tuple, List
import re
import nltk
from nltk.tokenize import word_tokenizer
import yaml
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

class ConceptDatabase:
    class ConceptLLMAPI:
        CURR_ENV_MAIN_CONCEPT_DELIMITER = "$CURR_ENV.MAIN_CONCEPT$" # TODO: Add tutor plan string to the llm request
        CURR_ENV_CONCEPT_LIST_DELIMITER = "$CURR_ENV.CONCEPT_LIST$"
        CONCEPT_NAME_DELIMITER = "$TARGET_CONCEPT_NAME$"

        def __init__(self, prompt_file, tutor_plan):
            self.__tutor_plan = tutor_plan
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.__prompt_template = "\n".join(f.readlines())
        def __get_prompt(self, main_concept, concept_list, concept_name):
            prompt = self.__prompt_template
            prompt = prompt.replace(self.CURR_ENV_MAIN_CONCEPT_DELIMITER, main_concept).replace(self.CURR_ENV_CONCEPT_LIST_DELIMITER, concept_list,).replace(self.CONCEPT_NAME_DELIMITER, concept_name,)
            return prompt
        
        def request_concept_data_from_llm(self, env_main_concept, env_concept_list, concept_name):
            """Requests the Concept information from an LLM.

            Args:
                env_main_concept (str): _description_ 
                env_concept_list (str): _description_
                concept_name (str): _description_

            Returns:
                _type_: _description_
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                    "role": "system",
                    "content": "You are an AI Tutor trying to tutor a student in a specific subject."
                    },
                    {
                    "role": "user",
                    "content": self.__get_prompt(self.__tutor_plan, env_main_concept, env_concept_list, concept_name)
                    },
                ],
                temperature=1,
                max_tokens=2600,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )
            return response
            
    __CONCEPT_REGEX = re.compile(r'\`\`\`yaml([^\`]*)\`\`\`') # Matches any ```yaml ... ```
    def __init__(self, main_concept:str):
        self.concept_llm_api = self.ConceptLLMAPI("src/TutorUtils/Prompts/concept_prompt")
        self.main_concept = main_concept
        self.Concepts = []
        self.generate_concept(self.main_concept,)
    
    def get_concept_list_str(self,):
        "\n".join([f"\t- \"{concept.name}\"" for concept in self.concepts],)
    
    def generate_concept(self, concept_name, max_depth=4):
        """
        Generates a Concept from a LLM
        """
        if max_depth == 0: 
            return 0# Some API call to LLM
        llm_output = self.concept_llm_api.request_concept_data_from_llm(self.main_concept, self.get_concept_list_str(), concept_name)
        regex_match = ConceptDatabase.__CONCEPT_REGEX.findall(llm_output)
        assert regex_match, f"Error parsing LLM Output for Concept: {concept_name}"
        # Extract the Yaml Data from the LLM Ouput
        m_start, m_end = regex_match[0].start(), regex_match[0].end()
        yaml_data = llm_output[m_start+len("```yaml"):m_end-len("```")].strip()
        parsed_data = yaml.safe_load(yaml_data)
        # Type check
        assert isinstance(parsed_data, dict), "Root should be a dictionary"
        # Key check
        assert 'Concept' in parsed_data, "Concept field is missing in the YAML data"
        assert all(key in parsed_data['Concept'] for key in ['name', 'definition',]), "Some required keys are missing in Concept"
        # Extract info from LLM Output        
        c_name = parsed_data["Concept"]['name']
        c_def = parsed_data["Concept"]["definition"]
        c_latex =  parsed_data["Concept"].get("latex_code", None)

        new_concept = Concept.from_concept_string(c_name, c_def, c_latex, self, max_depth-1)
        self.Concepts.append(new_concept)       

     
class Concept:
    def __init__(self, name:str):
         self.name = name
         self.definition = None
         self.refs = None
         self.latex = None

    @staticmethod
    def from_concept_string(concept_name: str, definition_str: str, latex_code:str, ConceptDatabase: ConceptDatabase, curr_max_depth = 3) -> 'Concept':
        """
        Creates a Concept from a tokenized concept string.

        Parameters:

         - concept_name: Name of the concept being created. 
         - definition_str: Tokenized/Formatted Concept definition string 
         - latex_code: The LaTeX representation of a concept, if applicable.
         - ConceptDatabase: a Database of concepts 
         Returns:

         - Concept: The concept being created.

         Example:

         concept_name: 

        """

        