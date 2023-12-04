import json
from typing import List, Tuple, Union
import re
from enum import IntEnum
import threading
import openai
from AITutor_Backend.src.BackendUtils.json_serialize import *
from AITutor_Backend.src.BackendUtils.json_serialize import JSONSerializable
from AITutor_Backend.src.TutorUtils.concepts import *

from enum import IntEnum
from typing import List, Tuple

import os
DEBUG = os.environ.get("DEBUG", 0)

SLIDE_CONTENT_PROMPT = """You now have a new Task; With the provided Slide Plan and the learning environment above, you will translate the Slide Plan into the Content Section that will be displayed on the Slide Layout for the current slide during your lecture. This should be a bulleted and conccise overview of what you would normally see on a presentation slide for a lecture, and serve as a learning guide for your student. It is important you cover the essentials required for the student to understand the conceptual content presented to them. This content will be used to present data to the Student, who will be learning material which.
Our slides will appear visually like so:

Our Slide's Layout:

[Title Section (already created and provided to you)]
[Content Section (this is what you are creating right now)]

After you plan the Slide Content section, create a JSON object which we can parse for the Content, e.g. 

```json
{"content": "insert content here..."}
``` 

Examples in the Content: You should output a bulleted list of notes for the slide to contain. Do not include the Slide Title, as this is already included by default.

Include small examples of concept usage when introducing or exploring new concepts, such as for the Concept of Linked list you can include something like:
 (Node_1) -> (Node_2)

 Or such as for the Concept Chain Rule: 
 f(x) =  sin(2x), u = 2x, f(x) = sin(u), f(x)' = sin(u)' * u' = cos(u) * 2 = 2*cos(2x)
Another example is if a Concept can be thought of as a functional component of a larger system, such as the split method in Python. Here is an example demonstrating functionality:
 s = "some, string, split, with"; s.split(",") # -> ["some", " string", " split", " with"]
Or Boolean operator precedence in Python: 
# given a and b are ints
x = not a > b or a != b # -> (not (a>b)) or (a!=b) where parentesis demonstrate the precedence of operations
The goal is to provide academic displayment of the content.

Ensure your output contains a valid JSON Object.

You are inserting examples into the content. You are now going to create the content.

Output: 
"""

SLIDE_PRESENTATION_PROMPT = """You now have a new Task; With the provided Slide Plan and the learning environment above, create a spoken Presentation/Lecture to present the information to the Student. This should take the format of a conversational demonstration to the student the content of the slide in detail based on the Slide's Content listed below. This is spoken conversation between you and the student is meant to teach the student the learning content displayed below, remember this is conversational. Ensure your explanation is at the level of which the student currently understands the content being displayed. Additionally, try to connect the presentation language to the student's interests and goals if you are developoing an example or explanation.

This is a short context of previous slides. Understand that if you are in the middle of a presentation, your conversation should reflect this.

**Slide's Context (short collection of previous slides that came before this one)**: $SLIDE_CONTEXT$

Here is how the student will view the Slide which you are currently presenting.

Current Slide Layout:

[Title Section]
$TITLE$
[Content Section] 
$SLIDE_CONTENT$

First, come up with the spoken presentation based on the context of this slide and the content of the current slide.
After this, you need to convert the spoken presentation into a JSON Object. Ceate a JSON object which we can parse for the Presentation content, e.g. 
```json
{"presentation": "insert presentation conversation here..."}
```

Introduce the topic straight away and do not add any additional templating such as "AI Tutor:" or "Student:" to your response. Do not introduce yourself, just get straight to the content.

Remember this is one of many slides. Refer to the Slide Number below to understand which slide you are currently on. This is not the only slide in the presentation.
This is Slide $SLIDE_NUM$ of $TOTAL_SLIDES$ slides.

Ensure your output contains a valid JSON Object containing the 'presentation' key.

Output: """


DOC_SYSTEM_PROMPT= """## Environment Backstory and Call to Action
Take on the role of an expert and all-knowing Tutor named Rocky. You have previously developed a plan for a Slides Presentation related to teaching a student a topic. You will be tasked with generating a document for a student which the User will provide you. 

 We have set up a learning environment for you to aid you in the process of teaching the Student. In this environment, you have access to a Notebank, a Slide Window Context, and the Slide Plan for the slide being presented to you for this task. You have already generated the Slide's Description, which will also be available for you to see below. 

### Purpose of the Slide:
Refer to each section based on the Environment's current SlidePlan Purpose, i.e. the ENUM Value listed as Purpose: X, use this to refer to the documentation below:

**Introductory:** The Content should introduce a new Set of Concepts Provided in the Slide Description

**Relative:** The content should relate the Concepts Provided in the Slide Description

**Exploratory:** The Content should explore new concepts provided in the slide description by adding sub topics which we havent learned about to a larger topic, such as exploring the chain rule after learning what derivatives are.

**Explanative:** The Content should explain the Concepts provided in the Slide Description.

**Examplative:** The Content should provide an example to the student based on the Slide Description.

## Assessing the Environment
- **Current SlidePlan:**
Reflect on SlidePlan provided; 
    - What is the Title?
    - What is the Purpose Statement requiring for you to do? This should fall under one of the above categories.
    - What are the Concepts? This should be related to the Slide Description you've already created.

- **Notebank:** This Notebank is a plan you have previously developed to help you with this process. Use it to assess what the student wants to learn and/or focus on in the lesson. Whatever plan you have created already, you should aim to stick by it. The student's Slide Preference Statement is important to pay attention to as it is their preferences for how the Slide Material should be presented to them.

- **Slide Description**: You should base the document off of the Slide Description which the Assistant has already created. This is to be thought of as your plan for the slide.

## Environment
- **Notebank**:
<Notebank>
$ENV.NOTEBANK_STATE$
</Notebank>

- **Current SlidePlan**:
<SlidePlan>
$ENV.SLIDE_PLAN$
</SlidePlan>

"""

class Purpose(IntEnum):
    Introductory = 0
    Relative = 1
    Exploratory = 2
    Explanative = 3
    Examplative = 4

class Slide(JSONSerializable, SQLSerializable):
    __SLIDE_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    def __init__(self, title: str, description: str, presentation: str, content: str, latex_codes: List[Tuple[str, str]], purpose: Purpose, purpose_statement: str, concepts: List[Concept]):
        self.title = title
        self.description = description
        self.presentation = presentation
        self.content = content
        self.latex_codes = latex_codes
        self.purpose = purpose
        self.purpose_statement = purpose_statement
        self.concepts = concepts

    def format_json(self):
        return {
            "title": self.title,
            "presentation": self.presentation,
            "content": self.content,
            "latex_codes": self.latex_codes,
            "purpose": self.purpose,
            "purpose_statement": self.purpose_statement,
            "concepts": [concept.name for concept in self.concepts]
        }
    
    def to_sql(self): #TODO: Latex Code, [[f"{l[0]}[SPA]{l[1]}"] for l in self.latex_codes]
        """
        Returns the Slide Object in SQL Format
        TODO: Implement Latex Code into Slides
        """
        return (self.title, self.description, self.presentation, self.content, "", int(self.purpose), self.purpose_statement, [c.name for c in self.concepts])
    @staticmethod
    def from_sql(title, description, presentation, content, ltx_codes, purpose, purpose_statement, concepts):
        """
        Builds a slide from SQL Format
        """
        return Slide(title, description, presentation, content, ltx_codes, Purpose(purpose), purpose_statement, concepts)
     
    @staticmethod
    def parse_llm_for_content(llm_output: str):
        """
        Returns (True, description) if Successful, (False, Error) otherwise. 
        """
        regex_match = Slide.__SLIDE_REGEX.findall(llm_output)
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        slideplan_data = regex_match if regex_match else llm_output
        try:
            slideplan_data = json.loads(slideplan_data)
        except json.JSONDecodeError:
            return False, f"Error parsing JSON on output: {llm_output},  Ensure your response was in JSON Format"
        s_content = slideplan_data.get('content', "content was not a valid entry.")
        if s_content and isinstance(s_content, list): s_content = "\n".join(s_content)
        return "content" in slideplan_data, s_content

    @staticmethod
    def parse_llm_for_presentation(llm_output: str):
        """
        Returns (True, presentation) if Successful, (False, Error) otherwise. 
        """
        regex_match = Slide.__SLIDE_REGEX.findall(llm_output)
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        slideplan_data = regex_match if regex_match else llm_output
        try:
            slideplan_data = json.loads(slideplan_data)
        except json.JSONDecodeError:
            return False, f"Error parsing JSON on output: {llm_output},  Ensure your response was in JSON Format"
        
        return "presentation" in slideplan_data, slideplan_data.get('presentation', "presentation was not a valid entry")

    
class SlidePlan(JSONSerializable):
    __SLIDEPLAN_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    PURPOSE_MAP_STR = {0: "INTRODUCTORY (0)", 1:"RELATIVE (1)", 2:"EXPLORATORY (2)", 3: "EXPLANATIVE (3)", 4: "EXAMPLATIVE (4)"}
    def __init__(self, title: str, purpose: Purpose, purpose_statement: str, concepts: List[Concept]):
        self.title = title
        self.purpose = purpose
        self.purpose_statement = purpose_statement
        self.concepts = concepts

    def format_json(self):
        return {
            "title": self.title,
            "purpose": self.purpose,
            "purpose_statement": self.purpose_statement,
            "concepts": [concept.name for concept in self.concepts]
        }
    
    def env_string(self,):
        return f"Title: {self.title}\nPurpose: {self.PURPOSE_MAP_STR[self.purpose]}\nPurpose Statement:{self.purpose_statement}\n"
    
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
        assert purpose != -1 and 0 <= purpose <= 4, "Purpose did not map correctly, ensure you have provided a valid ENUM Value."

        # Validating the purpose statement
        purpose_statement = slideplan_data.get('purpose_statement')
        assert purpose_statement and type(purpose_statement) == str, "Invalid or missing purpose statement in SlidePlan JSON data"

        # Validating the concepts
        concept_names = slideplan_data.get('concepts')
        assert concept_names and type(concept_names) == list, "Invalid or missing concepts in SlidePlan JSON data"
        
        concepts = [ConceptDatabase.get_concept(name) for name in concept_names]
        concepts = [c for c in concepts if c is not None and isinstance(c, Concept)]
        assert concepts, "One or more concepts are not recognized in SlidePlan JSON data"

        return SlidePlan(title, purpose, purpose_statement, concepts)

class SlidePlanner(JSONSerializable, SQLSerializable):
    class SlideLLMAPI:
        SLIDE_PLAN_SET_DELIMITER = "$ENV.SLIDE_PLAN_SET$" #Environment for the notebankd
        EXPLORED_CONCEPTS_DELIMITER = "$ENV.CONCEPTS_EXPLORED_VALUES$" #Environment for the chat history
        NOTEBANK_STATE_DELIMITER = "$ENV.NOTEBANK_STATE$"
        CURR_ENV_CONEPT_LIST = "$ENV.CONCEPT_LIST$"
        CURR_ENV_SLIDE_PLAN = "$ENV.SLIDE_PLAN$"
        CURR_ENV_CONEPT_DATA_DELIMITER = "$ENV.CONCEPT_DATA$"


        def __init__(self, slideplan_plan_prompt_file, slideplan_plan_to_obj_prompt_file, sideplan_terminate_prompt_file, slide_description_prompt_file):
            self.client = openai.OpenAI() if USE_OPENAI else ReplicateAPI()
            with open(slideplan_plan_prompt_file, "r") as f:
                self.__slideplan_plan_prompt = f.read()
            with open(slideplan_plan_to_obj_prompt_file, "r") as f:
                self.__slideplan_plan_to_obj_prompt = f.read()
            with open(sideplan_terminate_prompt_file, "r") as f:
                self.__sideplan_terminate_prompt = f.read()
            with open(slide_description_prompt_file, "r") as f:
                self.__slide_description_prompt = f.read()
                
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
            
        def conversational_JSON_request(self, system, assistant, user, model: str, max_length = 4000):
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
                            "content": system,
                        },
                        {
                            "role": "assistant",
                            "content": assistant,
                        },
                        {
                            "role": "user",
                            "content": user,
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
                return self.client.get_output(system, "[ASSISTANT]"+assistant+"[ASSISTANT]\n"+ + "[USER]" + user+"[/USER]")
            
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
        
        def prompt_terminate_slideplan(self, side_plan_set, explored_concepts, notebank_state):
            env_state = {SlidePlanner.SlideLLMAPI.SLIDE_PLAN_SET_DELIMITER: side_plan_set, SlidePlanner.SlideLLMAPI.EXPLORED_CONCEPTS_DELIMITER: explored_concepts, SlidePlanner.SlideLLMAPI.NOTEBANK_STATE_DELIMITER:notebank_state}
            return self._load_prompt(self.__sideplan_terminate_prompt, env_state)
        
        def prompt_sLideplan_to_obj(self, slide_plan):
            env_state = {"$SLIDE_PLAN$": slide_plan}
            return self._load_prompt(self.__slideplan_plan_to_obj_prompt, env_state)

        def prompt_sideplan_description(self, slide_plan_ref: SlidePlan, notebank_str:str ):
            def get_concept_data_str(p:SlidePlan): 
                return "\n".join([f"Concept: {c.name}\nDefinition: {c.to_tokenized_def()}\n\n" for c in  p.concepts])
            
            env_state = {SlidePlanner.SlideLLMAPI.CURR_ENV_SLIDE_PLAN: slide_plan_ref.env_string(), SlidePlanner.SlideLLMAPI.CURR_ENV_CONEPT_DATA_DELIMITER: get_concept_data_str(slide_plan_ref), SlidePlanner.SlideLLMAPI.NOTEBANK_STATE_DELIMITER: notebank_str}
            return self._load_prompt(self.__slide_description_prompt, env_state)
        
    def __init__(self, Notebank, ConceptDatabase):
        self.SlidePlans = []
        self.Slides = []
        self.Notebank = Notebank
        self.ConceptDatabase = ConceptDatabase
        self.num_slides = 0
        self.current_obj_idx = 0
        self.llm_api = SlidePlanner.SlideLLMAPI("AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/slideplan_plan_prompt", "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/slideplan_to_obj_prompt","AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/slide_plan_termination_prompt", "AITutor_Backend/src/TutorUtils/Prompts/KnowledgePhase/slide_description_prompt") # LLM API for generating slide plans
    def to_sql(self):
        return (self.current_obj_idx, self.num_slides, [slide.to_sql() for slide in self.Slides])
    
    @staticmethod
    def from_sql(current_obj_idx, num_slides, slides, notebank, concept_database):
        slide_planer = SlidePlanner(notebank, concept_database)
        slide_planer.current_obj_idx = current_obj_idx
        slide_planer.num_slides = num_slides
        slide_planer.Slides = [Slide.from_sql(s[0], s[1], s[2], s[3], s[4], s[5], s[6], [concept_database.get_concept(cpt) for cpt in s[7]]) for s in slides]
        return slide_planer

    def format_json(self,):
        return {"slides": [slide.format_json() for slide in self.Slides], "current_obj_idx": self.current_obj_idx, "num_slides": self.num_slides}
    
    def get_object(self, idx):
        """
        Returns Slide Object iff idx is a valid Slide Object index. Else, AssertionError
        """
        assert 0 <= idx < self.num_slides, "Cannot access Slide Object Array Out of Bounds"
        return self.Slides[idx]

    def generate_slide_plan(self):
        if DEBUG: print(f"Generating Slide Plan for {self.ConceptDatabase.main_concept}")
        notebank_state = self.Notebank.env_string()
        while True:
            # Prepare input for LLM
            slideplan_prompt = self.llm_api.prompt_plan_slideplan(self._generate_slideplans_str(), self._generate_concept_exploration_map_str(), notebank_state)
            # Request output from LLM
            llm_output = self.llm_api.request_output_from_llm(slideplan_prompt, "gpt-4-1106-preview")    
            # Convert:
            conversion_prompt = self.llm_api.prompt_sLideplan_to_obj(llm_output)
            error = "There currently is no error."
            for i in range(5):
                try:
                    llm_output = self.llm_api.request_output_from_llm(conversion_prompt, model="gpt-3.5-turbo-16k")    
                    slide_plan = SlidePlan.create_slideplan_from_JSON(llm_output, self.ConceptDatabase)
                    break
                except Exception as err: # TODO: Fix error handling
                    error = str(err)
            self.SlidePlans.append(slide_plan)
            slideplan_prompt = self.llm_api.prompt_terminate_slideplan(self._generate_slideplans_str(), self._generate_concept_exploration_map_str(), notebank_state)
            llm_output = self.llm_api.request_output_from_llm(slideplan_prompt, "gpt-4-1106-preview")    
            if "[TERM]" in llm_output:
                break

    def generate_slide(self, slide_plan:SlidePlan, index, results, generation_lock):
        notebank_state = self.Notebank.env_string()
        # Prepare Slide Description Prompt
        slide_prompt = self.llm_api.prompt_sideplan_description(slide_plan, notebank_state)
        # Request output from LLM
        s_description = self.llm_api.request_output_from_llm(slide_prompt, "gpt-4-1106-preview")
        # Try to get content:
        # content_prompt = slide_prompt+"\n\nAI Tutor:\n"+s_description+"\n\nSystem:\n"+SLIDE_content_PROMPT
        system_prompt = DOC_SYSTEM_PROMPT.replace("$ENV.SLIDE_PLAN$", slide_plan.env_string()).replace("$ENV.NOTEBANK_STATE$", notebank_state)
        while True:
            llm_output = self.llm_api.conversational_JSON_request(system_prompt, s_description, SLIDE_CONTENT_PROMPT, "gpt-4-1106-preview")
            success, s_content = Slide.parse_llm_for_content(llm_output)
            if success: break
        # Try to get Presentation:
        # presentation_prompt = slide_prompt+"\n\nAI Tutor:\n"+s_description+"\n\nSystem:\n"+SLIDE_PRESENTATION_PROMPT
        while True:
            llm_output = self.llm_api.conversational_JSON_request(system_prompt, s_description, SLIDE_PRESENTATION_PROMPT.replace("$TITLE$", slide_plan.title).replace("$SLIDE_CONTENT$", s_content).replace("$SLIDE_NUM$ of $TOTAL_SLIDES$", f"{index+1} of {self.num_slides}"), "gpt-4-1106-preview")
            success, s_presentation = Slide.parse_llm_for_presentation(llm_output)
            if success: break
        n_slide = Slide(title=slide_plan.title, description=s_description, presentation=s_presentation, content=s_content, latex_codes="", purpose=slide_plan.purpose, purpose_statement=slide_plan.purpose_statement, concepts=slide_plan.concepts.copy())
        with generation_lock: # Data sensitive 
            results.append((index, n_slide))
            if DEBUG: print("Created Slide:", n_slide.format_json())
            self.num_slides+=1
    
    def generate_slide_deque(self,):
        results = []
        threads = []
        generation_lock = threading.Lock()
        for (idx, slide_plan_ref) in enumerate(self.SlidePlans):
            thread = threading.Thread(target=self.generate_slide, args=(slide_plan_ref, idx, results, generation_lock))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Sort and Save Results
        results.sort(key=lambda x: x[0])
        self.Slides = [r[1] for r in results]
        

    def _generate_slideplans_str(self):
        return '\n'.join([f"{slide_plan.title}: {slide_plan.purpose}, {slide_plan.purpose_statement}, Concepts: {', '.join([c.name for c in slide_plan.concepts if c is not None])}" for slide_plan in self.SlidePlans])

    def _generate_concept_exploration_map_str(self):
        return '\n'.join([f"{concept.name}: {sum([1 for slide_plan in self.SlidePlans if concept in slide_plan.concepts])}" for concept in self.ConceptDatabase.Concepts])
    
    def _generate_slide_window_context(self, idx):
        """
        [curr]
        """
        newline = "\n"
        s = """[Previous Slides]\n""" + \
            f"""[{f'{newline+newline}'.join([f"Previous Slide: {newline}"+str(slide.format_json()) for i, slide in enumerate(self.SlidePlans[max(0, idx-2):idx])])}]"""+ "\n[/Previous Slides]"
        if idx == self.num_slides-1: s+= "This is the Last Slide in the deque. Consider adding closing Remarks."
        
        s+= """\n[Upcoming Slides]"""+f"""[{f'{newline+newline}'.join([f"Previous Slide: {newline}"+str(slide.format_json()) for i, slide in enumerate(self.SlidePlans[max(idx+1, self.num_slides-1):max(self.num_slides-1, idx+3)])])}]"""+ "\n[/Upcoming Slides]" if s != self.num_slides-1 else "This is the last slide."
        return s
