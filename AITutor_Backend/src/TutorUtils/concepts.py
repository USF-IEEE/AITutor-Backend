from typing import Tuple, List
import re
import yaml
import os
import openai

from AITutor_Backend.src.BackendUtils.replicate_api import ReplicateAPI
from AITutor_Backend.src.DataUtils.nlp_utils import edit_distance
from AITutor_Backend.src.BackendUtils.sql_serialize import SQLSerializable

USE_OPENAI = True


class ConceptDatabase(SQLSerializable):
    class ConceptLLMAPI:
        CURR_ENV_MAIN_CONCEPT_DELIMITER = "$CURR_ENV.MAIN_CONCEPT$" # TODO: Add tutor plan string to the llm request
        CURR_ENV_CONCEPT_LIST_DELIMITER = "$CURR_ENV.CONCEPT_LIST$"
        CONCEPT_NAME_DELIMITER = "$TARGET_CONCEPT_NAME$"
        TUTOR_PLANNER_DELIMITER = "$CURR_ENV.TUTOR_PLANNER$"
        CURR_ERROR_DELIMITER = "$CURR_ENV.ERROR$"

        def __init__(self, prompt_file, tutor_plan):
            self.__tutor_plan = tutor_plan
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.__prompt_template = "\n".join(f.readlines())
            
            self.client = openai.OpenAI() if USE_OPENAI else ReplicateAPI()
            
        def __get_prompt(self, tutor_plan, main_concept, concept_list, concept_name, error_msg):
            prompt = self.__prompt_template
            prompt = prompt.replace(self.TUTOR_PLANNER_DELIMITER, tutor_plan).replace(self.CURR_ENV_MAIN_CONCEPT_DELIMITER, main_concept).replace(self.CURR_ENV_CONCEPT_LIST_DELIMITER, concept_list,).replace(self.CONCEPT_NAME_DELIMITER, concept_name,).replace(self.CURR_ERROR_DELIMITER, error_msg)
            return prompt
        
        def request_concept_data_from_llm(self, env_main_concept, env_concept_list, concept_name, error_msg):
            """Requests the Concept information from an LLM.

            Args:
                env_main_concept (str): _description_ 
                env_concept_list (str): _description_
                concept_name (str): _description_

            Returns:
                str: LLM Output containing Concept Data
            """
            prompt = self.__get_prompt(self.__tutor_plan, env_main_concept, env_concept_list, concept_name, error_msg)
                
            # model = "gpt-3.5-turbo-1106" #if concept_name != env_main_concept else "gpt-4"
            if USE_OPENAI:
                model = "gpt-4"
                # model = "gpt-3.5-turbo-16k"
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": prompt,
                        },
                    ],
                    temperature=0.9,
                    max_tokens=3000,
                    top_p=0.9,
                    frequency_penalty=0,
                    presence_penalty=0,
                )

                return response.choices[0].message.content
            else:
                return self.client.get_output(prompt, " ")
        
            
    __CONCEPT_REGEX = re.compile(r'\`\`\`yaml([^\`]*)\`\`\`') # Matches any ```yaml ... ```
    def __init__(self, main_concept:str, tutor_plan:str = "", generation=True):
        self.concept_llm_api = self.ConceptLLMAPI("AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/concept_prompt", tutor_plan=tutor_plan) # TODO: FIX
        self.main_concept = main_concept
        self.Concepts = []
        if generation:
            self.generate_concept(self.main_concept,)
    
    def get_concept_list_str(self,):
        return "\n".join([f"\t- \"{concept.name}\"" for concept in self.Concepts],) if self.Concepts else "The Concept List is Empty."
    
    def get_concept(self, concept_name:str): # We use edit distance of 4 as a max
        concept = [(edit_distance(concept_name.lower(), concept.name.lower()), concept) for concept in self.Concepts if edit_distance(concept_name.lower(), concept.name.lower()) < 4]
        if concept: concept.sort(key=lambda x: x[0])# Get the best match
        return concept[0][1] if concept else None
    
    def generate_concept(self, concept_name, max_depth=4):
        """
        Generates a Concept from a LLM
        """
        def escape_backslashes_in_quotes(text):
            def replace_backslashes(match):
                return match.group(0).replace('\\', '\\\\')
            quoted_strings_regex = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
            return re.sub(quoted_strings_regex, replace_backslashes, text)
            
        if max_depth == 0: 
            return 0# Some API call to LLM
        error_msg = "There is no current error detected in the parsing system."
        while True:
            llm_output = self.concept_llm_api.request_concept_data_from_llm(self.main_concept, self.get_concept_list_str(), concept_name, error_msg)
            try:
                regex_match = ConceptDatabase.__CONCEPT_REGEX.findall(llm_output)
                assert regex_match, f"Error parsing LLM Output for Concept: {concept_name}. Ensure you properly used the Yaml Creation rules."
                # Extract the Yaml Data from the LLM Ouput
                parsed_data = escape_backslashes_in_quotes(regex_match[0])
                parsed_data = yaml.safe_load(parsed_data)
                # Type check
                assert isinstance(parsed_data, dict), "Root should be a dictionary"
                # Key check
                assert 'Concept' in parsed_data, "Concept field is missing in the YAML data"
                assert all(key in parsed_data['Concept'] for key in ['name', 'definition',]), "Some required keys are missing in Concept"
                # Extract info from LLM Output        
                c_name = parsed_data["Concept"]['name']
                c_def = parsed_data["Concept"]["definition"]
                c_latex =  parsed_data["Concept"].get("latex_code", None)
                if c_latex and (c_latex.lower() == "none" or c_latex.lower() == "null"): c_latex = "" 
                new_concept = Concept.create_from_concept_string_add_to_database(c_name, c_def, c_latex, self, max_depth-1)    
                if max_depth == 0: break
                assert new_concept, "Could not create concept from LLM Output, ensure you have properly entered the information and did not include any additional information outside of what's required."
                break
            except Exception as e:
                error_msg = str(e)
                
    @staticmethod                
    def from_sql(main_concept, tutor_plan, concepts):
        """creates a ConceptDatabase from sql data.

        Args:
            main_concept (str): _description_
            tutor_plan (str): plan from tutor
            concepts (List[str, str, str]): List[(concept_name, concept_def, concept_latex)] 

        Returns:
            _type_: ConceptDatabase
        """
        cd = ConceptDatabase(main_concept, tutor_plan, generation=False)
        cd.Concepts = [Concept(cpt[0], cpt[2]) for cpt in concepts]
        
        # Map the Graph:
        for cpt_ref, cpt_data in zip(cd.Concepts, concepts):
            def_sequence = [] # Where our tokens live
            #Get all tokens from definition string, string or concept format
            pattern = re.compile(r'<Concept>.*?<\/Concept>|\S+')
            tokens = pattern.findall(cpt_data[1]) # Look through tokenized definition string
            #Find concepts in main concept's definition using regex
            for token in tokens:
                if '<Concept>' in token:
                    c_name = token.replace("<Concept>", "").replace("</Concept>", "")
                    existing_concept = cd.get_concept(c_name)
                    def_sequence.append(existing_concept) if existing_concept else def_sequence.append(c_name)     
                else: # Token is just a word
                    def_sequence.append(token)
            # Update our Concept:
            cpt_ref.set_definition(def_sequence)
        return cd
    
    def to_sql(self, ):
        """
        Returns:
            main_concept (str): 
            concepts (List[str, str, str]): List[(concept_name, concept_def, concept_latex)]
        """
        return (self.main_concept, [c.to_sql() for c in self.Concepts])
        
        
     
class Concept:
    def __init__(self, name:str, latex:str):
         self.name = name
         self.definition = ""
         self.refs = []
         self.latex = latex if latex else ""

    def __repr__(self) -> str:
        return f"Concept(name: {self.name}) <{self.__hash__()}>"
    
    def set_definition(self, definition):
        self.definition = definition
        self.refs = [tkn for tkn in self.definition if isinstance(tkn, Concept)]

    @staticmethod
    def create_from_concept_string_add_to_database(concept_name: str, definition_str: str, latex_code:str, ConceptDatabase: ConceptDatabase, curr_max_depth = 3) -> 'Concept':
        """
        Creates a Concept from a tokenized concept string and adds it to the ConceptDatabase provided.

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

        if curr_max_depth < 0:
            return None
        
        def_sequence = [] # Where our tokens live

        # Create and add Main Concept(name) to Database:
        concept = Concept(concept_name, latex_code)
        ConceptDatabase.Concepts.append(concept)  

        #Get all tokens from definition string, string or concept format
        pattern = re.compile(r'<Concept>.*?<\/Concept>|\S+')
        tokens = pattern.findall(definition_str)
        #Find concepts in main concept's definition using regex
        for token in tokens:
            if '<Concept>' in token:
                c_name = token.replace("<Concept>", "").replace("</Concept>", "")
                c_name.replace('\\', "")
                existing_concept = ConceptDatabase.get_concept(c_name)
                # Map concepts together if both exist on the same database (avoid duplicates)
                # Check if the concept already exists in the database to avoid duplicates  
                if not existing_concept:
                    # If the concept does not exist, create a new one with reduced depth
                    existing_concept = ConceptDatabase.generate_concept(concept_name=c_name, max_depth=curr_max_depth)
                def_sequence.append(existing_concept) if existing_concept else def_sequence.append(c_name)     
            else: # Token is just a word
                def_sequence.append(token)
        # Update our Concept:
        concept.set_definition(def_sequence)
        return concept
    
    def to_sql(self,) -> Tuple[str, str, str]:
        """Returns the state of Concept

        Returns:
            Tuple[str, str, str]: (concept_name, concept_def, concept_latex) 
        """
        map_word = lambda x: x if isinstance(x, str) else "<Concept>"+x.name+"</Concept>"
        return (self.name, " ".join([map_word(cpt) for cpt in self.definition]), self.latex,)
    