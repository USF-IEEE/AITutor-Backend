from typing import Tuple, Union, List
from enum import IntEnum
import re

class NoteBank:
    __NOTEBANK_REGEX = re.compile(r'\`\`\`notebank([^\`]*)\`\`\`')
    class Op(IntEnum):
        ADD=0
        DEL=1
        NOP=2
    def __init__(self,):
        self.__notes = []

    @staticmethod
    def __extract_operation(llm_output:str)-> List[Tuple['NoteBank.Op', Union[int, str]]]:
        """
        Extracts an operation from an LLM Output containing 
        """
        regex_match = NoteBank.__NOTEBANK_REGEX.findall(llm_output)
        assert regex_match, f"Error parsing LLM Output for NoteBank Operation: {llm_output}"
        # Format the regex match to a parsable string
        regex_match = regex_match[0].replace("```notebank", "").replace("```", "").strip() 
        # Extract the Operation data from the LLM Ouput
        #   1. Extract tokens and Validate Input, 
        #   2. decide operation and data
        try:
            tokens = [t_set.replace(" ", "$$", 1).split("$$") for t_set in regex_match.split("\n")] # Replace first \sp with a token for splitting on.
        except Exception as e:
            raise Exception(f"Error: Could not parse Tokens, {str(e)}")
        # Assert our tokens have been parsed correctly
        for t in tokens:
            assert len(t) == 2, "Error Parsing Tokens"
        for (op, val) in tokens: 
            # Determine and return operation
            yield (NoteBank.Op.DEL, int(re.sub("[^\d]","", val))) if op.lower() == "del" else (NoteBank.Op.ADD, val)
    
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
        
    def process_tutor_action(self, llm_output:str) -> Tuple[bool, str]: 
        """
        This function will attempt to modify the data structure based on the Tutor's action. 
        
        Parameters:
            - llm_output: (str) The Tutor's action represented in terms of a token-string

        Returns:
            - True, \"\" iff the actions were successfully parsed
            - False, error_str iff there was an error in the Parsing or Execution
        """
        try:
            # Process inputs:
            operations = NoteBank.__extract_operation(llm_output=llm_output)
            # Iterate through operations:
            for operation in operations:
                self.__exec_op(operation[0], operation[1]) # Executes operation for the tutor
            return True, ""
        except Exception as e:
            return False, str(e) # Output will be provided to the model in the case that there was an error; See (INSERT REFERENCE TO VOYAGER HERE)

    def env_string(self,):
        """
        Returns Environment Observation String which the model will use for prediction.
        """
        return "\n".join([f"[{i}]: {val}" for i, val in enumerate(self.__notes)]) if self.__notes else "NoteBank is Empty."
    
    def size(self,) -> int:
        """Returns size of the Notebank"""
        return len(self.__notes)