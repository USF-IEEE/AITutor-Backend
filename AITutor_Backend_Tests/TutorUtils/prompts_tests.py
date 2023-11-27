import unittest
from AITutor_Backend.src.TutorUtils.prompts import *

class PromptTests(unittest.TestCase):
    def test_prompt_parsing_from_llm_output(self):
        json_output1 = '```json\n{"type": "text", "prompt": "Please detail further what piece of this subject is troubling you the most."}\n```'
        
        json_output2 = '```json\n{"type": "terminate", "prompt": "End of Tutor\'s PromptActions for this session."}\n```'
        
        json_output3 = '{"type": "file", "prompt": "Please submit the lecture notes from the course you wish to go into further detail on."}'
        
        json_output4 = '```json\n{"type": "rating", "prompt": "How interested are you on a scale from [0-5] in learning about Time Complexities for each algorithm?"}\n```'

        p1 = PromptAction.parse_llm_action(json_output1)
        self.assertEqual(p1.format_json()["type"], PromptAction.Type.TEXT.value, "Error in parsing Text prompt.")

        p2 = PromptAction.parse_llm_action(json_output2)
        self.assertEqual(p2.format_json()["type"], PromptAction.Type.TERMINATE.value, "Error in parsing Termination prompt.")
        
        p3 = PromptAction.parse_llm_action(json_output3)
        self.assertEqual(p3.format_json()["type"], PromptAction.Type.FILE.value, "Error in parsing File prompt.")
        
        p4 = PromptAction.parse_llm_action(json_output4)
        self.assertEqual(p4.format_json()["type"], PromptAction.Type.RATING.value, "Error in parsing Rating prompt.")

        # Additional test case for invalid input can be added if desired
