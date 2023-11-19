from typing import Tuple, Union, List
from enum import IntEnum
import json
import re

class NoteBank:
    __NOTEBANK_REGEX = re.compile(r'\`\`\`json([^\`]*)\`\`\`')
    class Op(IntEnum):
        ADD=0
        DEL=1
        NOP=2
        TERMINATE=3
    def __init__(self,):
        self.__notes = []

    @staticmethod
    def __extract_operation(llm_output:str)-> List[Tuple['NoteBank.Op', Union[int, str]]]:
        """
        Extracts an operation from an LLM Output containing 
        """

        regex_match = NoteBank.__NOTEBANK_REGEX.findall(llm_output)        
        # Format the regex match to a parsable string
        if regex_match:
            regex_match = regex_match[0].replace("```json", "").replace("```", "").strip()
        prompt_data = regex_match if regex_match else llm_output
        try:
            actions = json.loads(prompt_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON: {str(e)}")

        for action in actions:
            action_type = action.get("action").lower()
            if action_type == "add":
                yield (NoteBank.Op.ADD, action["note"])
            elif action_type == "del":
                yield (NoteBank.Op.DEL, action["index"])
            elif action_type == "nop":
                yield (NoteBank.Op.NOP, "No Operation")
            elif action_type == "terminate":
                yield (NoteBank.Op.TERMINATE, "Terminate")
            else:
                raise ValueError(f"Unknown action type: {action_type}")
    
    def __exec_op(self, op: 'NoteBank.Op', val: Union[int, str]) -> None:
        """
        This function processes an operation on the Notebank
        """
        if op == self.Op.DEL:
            assert isinstance(val, int) and val > 0 and val < len(self.__notes), f"Error: Could not process delete on input {val}. Ensure this input is valid and is a valid index in the NoteBank" # Validate Index is valid removal
            del self.__notes[val]
        if op == self.Op.ADD:
            assert isinstance(val, str), "Error: Could not process add on input {val}. Ensure this input is of type Str."
            self.__notes.append(val) # insert into notebank

    def process_llm_action(self, llm_output:str) -> Tuple[bool, str, bool]: 
        """
        This function will attempt to modify the data structure based on the Tutor's action. 
        
        Parameters:
            - llm_output: (str) The Tutor's action represented in terms of a token-string

        Returns:
            - True, \"\", False iff the actions were successfully parsed
            - False, error_str, False iff there was an error in the Parsing or Execution
            - True, \"\", True to terminate on the Notebank.
        """
        terminate = False
        try:
            # Process inputs:
            operations = NoteBank.__extract_operation(llm_output=llm_output)
            # Iterate through operations:
            for operation in operations:
                if operation[0] == NoteBank.Op.TERMINATE: terminate = True
                self.__exec_op(op=operation[0], val=operation[1]) # Executes operation for the tutor
            return True, "", terminate
        except Exception as e:
            return False, str(e), False # Output will be provided to the model in the case that there was an error; See (INSERT REFERENCE TO VOYAGER HERE)

    def env_string(self,):
        """
        Returns Environment Observation String which the model will use for prediction.
        """
        return "{\"Notebank\": [" + "\n".join(["{" + f"\"index\": {i}, \"note\": \"{val}\""+ "}," for i, val in enumerate(self.__notes)]) + "]}" if self.__notes else "// the Notebank is Empty."
    
    def size(self,) -> int:
        """Returns size of the Notebank"""
        return len(self.__notes)
    
    def get_notes(self,) ->List[str]:
        return self.__notes.copy()
    
    def to_sql(self,):
        return "\n".join(self.__notes)
    
    @staticmethod
    def from_sql(sql_data):
        nb = NoteBank()
        nb.__notes = sql_data.split("\n")
        return nb