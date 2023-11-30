import re
import os
from typing import List
import openai
from AITutor_Backend.src.BackendUtils.replicate_api import ReplicateAPI
from enum import IntEnum
from AITutor_Backend.src.TutorUtils.notebank import NoteBank 
from AITutor_Backend.src.TutorUtils.chat_history import ChatHistory
from AITutor_Backend.src.BackendUtils.json_serialize import *
import json
USE_OPENAI = True

class Prompter:
    class PrompterLLMAPI:
        CURR_ENV_NOTEBANK_DELIMITER = "$NOTEBANK.STATE$" #Environment for the notebankd
        CURR_ENV_CHAT_HISTORY_DELIMITER = "$CHAT_HISTORY$" #Environment for the chat history 
        QUESTION_COUNTER_DELIMITER = "$NUM_QUESTIONS$"
        PLAN_DELIMITER = "$ACTION_PLAN$"
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


    def __init__(self, question_prompt_file, notebank_prompt_file, plan_prompt_file, notebank:NoteBank, chat_history:ChatHistory, debug=False):
        self.llm_api = self.PrompterLLMAPI() 
        self.notebank = notebank
        self.chat_history = chat_history
        self.__questions_asked = 0
        with open(question_prompt_file, "r", encoding="utf-8") as f:
            self.__question_prompt_template = "\n".join(f.readlines())

        with open(notebank_prompt_file, "r", encoding="utf-8") as f:
            self.__notebank_prompt_template = "\n".join(f.readlines())
        
        with open(plan_prompt_file, "r", encoding="utf-8") as f:
            self.__plan_prompt_template = "\n".join(f.readlines())
    
    def perform_plan(self, ):
        """
        Get Plan from a LLM
        """
        prompt = self.llm_api._load_prompt(self.__plan_prompt_template, {Prompter.PrompterLLMAPI.CURR_ENV_NOTEBANK_DELIMITER: self.notebank.env_string(), Prompter.PrompterLLMAPI.CURR_ENV_CHAT_HISTORY_DELIMITER: self.chat_history.env_string(), Prompter.PrompterLLMAPI.QUESTION_COUNTER_DELIMITER: str(self.__questions_asked), },) 
        llm_plan = self.llm_api.request_output_from_llm(prompt, "gpt-3.5-turbo-16k") #"gpt-4"
        return llm_plan
    
    def perform_notebank(self, plan):
        """
        Get Notebank Action from a LLM
        """
        error = "There is no current error."
        while True:
            prompt = self.llm_api._load_prompt(self.__notebank_prompt_template, {Prompter.PrompterLLMAPI.CURR_ENV_NOTEBANK_DELIMITER: self.notebank.env_string(), Prompter.PrompterLLMAPI.CURR_ENV_CHAT_HISTORY_DELIMITER: self.chat_history.env_string(), Prompter.PrompterLLMAPI.QUESTION_COUNTER_DELIMITER: str(self.__questions_asked), Prompter.PrompterLLMAPI.CURR_ERROR_DELIMITER: error, Prompter.PrompterLLMAPI.PLAN_DELIMITER: plan},) 
            llm_output = self.llm_api.request_output_from_llm(prompt, "gpt-3.5-turbo-16k")
            success, error, terminate = self.notebank.process_llm_action(llm_output)
            if success or terminate: break
        return terminate

    def get_prompting(self, plan):
        """
        Get Prompt Question from a LLM
        """  
        error = "There is no current error."      
        while True:
            try:
                prompt = self.llm_api._load_prompt(self.__question_prompt_template, {Prompter.PrompterLLMAPI.CURR_ENV_NOTEBANK_DELIMITER: self.notebank.env_string(),  Prompter.PrompterLLMAPI.CURR_ENV_CHAT_HISTORY_DELIMITER: self.chat_history.env_string(), Prompter.PrompterLLMAPI.QUESTION_COUNTER_DELIMITER: str(self.__questions_asked), Prompter.PrompterLLMAPI.CURR_ERROR_DELIMITER: error, Prompter.PrompterLLMAPI.PLAN_DELIMITER: plan})
                llm_output = self.llm_api.request_output_from_llm(prompt, "gpt-3.5-turbo-16k")
                action = PromptAction.parse_llm_action(llm_output)
                assert isinstance(action._type, PromptAction.Type), "Error while Creating the Prompt."
                assert action._data, "Error while parsing the data for the Prompt."
                break
            except Exception as e:
                error = "There was an error while trying to parse the Prompt: " + str(e)
        # Return the PromptAction parsed from the LLM:
        self.__questions_asked += 1
        return action
    
    
    def perform_tutor(self, student_input:str):
        """
        Cognitive Process
        """
        self.chat_history.hear(student_input) # DEBUGONLY: Remove this to include in TutorEnv
        # Construct the notebank:
        plan = self.perform_plan()
        print(f"\n[Plan]\n{plan}\n[/PLAN]\n")
        terminate = self.perform_notebank(plan)
        # Construct the prompting:
        llm_prompt = None
        if not terminate: 
            llm_prompt = self.get_prompting(plan)
            self.chat_history.respond(llm_prompt._data) # DEBUGONLY: Remove this to include in TutorEnv
            terminate = llm_prompt._type == PromptAction.Type.TERMINATE
        return llm_prompt, terminate


class PromptAction(JSONSerializable,):
    class Type(IntEnum):
        FILE=0
        TEXT=1
        RATING=2
        TERMINATE=-1
    __QUESTION_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    
    def __init__(self, prompt: str, type: 'PromptAction.Type', suggested_responses: List[str]):
        self._type = type
        self._data = prompt
        self._suggested_responses = suggested_responses
        

    def format_json(self):
        """
        Format into JSON Object:
        - type: ENUM (0-FILE, 1-TEXT, 2-RATING, (NEGATIVE)1-TERMINATE)
        - question: STR
        """
        return {"type": int(self._type), "question": self._data, "suggested_responses": self._suggested_responses.copy()}
    
    @staticmethod
    def parse_llm_action(llm_output: str) -> 'PromptAction':
        """
        Given LLM Output; parse for formattable Prompt Type and Question
        """
        regex_match = PromptAction.__QUESTION_REGEX.findall(llm_output)
        # Try to get json format or attempt to use output as json
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        prompt_data = regex_match if regex_match else llm_output
        try:
            action_data = json.loads(prompt_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON on output: {llm_output},  error: {str(e)}")

        action_type = action_data.get("type").lower()
        prompt = action_data.get("prompt")
        s_responses = action_data.get("suggested_responses", [])

        # Map the action type to the corresponding Type enum
        type_map = {
            "file": PromptAction.Type.FILE,
            "text": PromptAction.Type.TEXT,
            "rating": PromptAction.Type.RATING,
            "terminate": PromptAction.Type.TERMINATE
        }

        p_type = type_map.get(action_type, None)
        assert p_type is not None, "Error: Unknown action type."
        assert prompt, "Error: Prompt text is missing."

        return PromptAction(prompt, p_type, s_responses)
