import re
from enum import IntEnum
from src.BackendUtils.json_serialize import *

class PromptAction(JSONSerializable,):
    class Type(IntEnum):
        FILE=0
        TEXT=1
        RATING=2
        TERMINATE=-1
    __QUESTION_REGEX = re.compile(r'\`\`\`([Tt]ext|[Ff]ile|[Rr]ating)[Pp]rompt([^\`]*)\`\`\`|\[TERM\]') # Matches any Prompt String
    def __init__(self, question:str, type:'PromptAction.Type'):
        super(PromptAction, self).__init__()
        self._type = type
        self._data = question

    def format_json(self):
        """
        Format into JSON Object:
        - type: ENUM (0-FILE, 1-TEXT, 2-RATING, (NEGATIVE)1-TERMINATE)
        - question: STR
        """
        return {"type":int(self._type), "question":self._data}
    

    @staticmethod
    def parse_llm_action(llm_output:str,) -> 'PromptAction':
        """Given LLM Output; parse for formattable Prompt Type and Question"""
        regex_match = PromptAction.__QUESTION_REGEX.findall(llm_output)
        assert regex_match, f"Error parsing LLM Output for Prompt:\n {llm_output}"
        # Extract the Prompt Type & Data from the LLM Ouput
        m_start, m_end = regex_match[0].start(), regex_match[0].end()
        prompt_data = llm_output[m_start:m_end-len("```")].strip()
        # Detect if Termination Case:
        if "[TERM]" in prompt_data: return PromptAction("", PromptAction.Type.TERMINATE)
        # Get prompt type
        p_type = {"file", "rating", "text"}.get(llm_output.lower()[0+len("```"): llm_output.index("prompt")], None)
        assert p_type, "Error: Could not parse LLM for Prompt Action."
        type = {"file": PromptAction.Type.FILE, "rating": PromptAction.Type.RATING, "text": PromptAction.Type.TEXT}[p_type]
        # Get the question
        question = llm_output[len("```")+len(p_type)+len("prompt"):-len("```")].trim().strip()
        assert question, "Error: Could not parse LLM for Prompt Action."
        return PromptAction(question, type)


        