import unittest
from AITutor_Backend.src.TutorUtils.notebank import *

class NotebankTests(unittest.TestCase):
    def test_notebank_creation_and_modification(self,):
        notebank = NoteBank()
        action_1 = """
        ```json
        [
            {"action": "add", "note": "Needs more practice with differentiation."},
            {"action": "add", "note": "Maybe I should present the user with different techniques of differentiation and ask them to rank their comprehension in each."}
        ]
        ```
        """

        action_2 = """
        [
            {"action": "del", "index": 1},
            {"action": "add", "note": "User seems to understand Chain Rule and basic differentiation, but struggles with division differentiation."},
            {"action": "add", "note": "Overall, user should be given help with all types of differentiation."}
        ]
        """

        action_3 = """
        ```json
        [
            {"action": "del", "index": "BAD_DATA_1"},
            {"action": "add", "note": "User seems to understand Chain Rule and basic differentiation, but struggles with division differentiation."},
            {"action": "add", "note": "Overall, user should be given help with all types of differentiation."}
        ]
        ```
        """

        action_4 = """
        ```json
        [
            {"action": "del", "index": 10}
        ]
        ```
        """
        action_5 = """
        ```json
        [
            {"action": "terminate", "note": "End of Tutor's Notebank actions for this session."}
        ]
        ```
        """
        
        op_suc, err_msg, terminate = notebank.process_llm_action(action_1)
        self.assertTrue(op_suc, f"Error: unsuccessful notebank parse, {err_msg}")
        self.assertTrue(notebank.size() == 2, f"Error in parsing elements. Expected: 2, Actual: {notebank.size()}")
        self.assertFalse(terminate)

        op_suc, err_msg, terminate = notebank.process_llm_action(action_2)
        self.assertTrue(op_suc, f"Error: unsuccessful notebank parse, {err_msg}")
        self.assertTrue(notebank.size() == 3, f"Error in parsing elements. Expected: 3, Actual: {notebank.size()}")

        prev_size = notebank.size()
        op_suc, err_msg, terminate = notebank.process_llm_action(action_3)
        self.assertFalse(op_suc, "Error: failed to detect bad notebank parse.")
        self.assertEqual(notebank.size(), prev_size, f"Additional elements added during bad parsing. Expected Size: {prev_size}, Actual Size: {notebank.size()}")
        
        op_suc, err_msg, terminate = notebank.process_llm_action(action_4)
        self.assertFalse(op_suc, "Failed to reject bad input (index 10) Index Out of Bounds.")  
        
        op_suc, err_msg, terminate = notebank.process_llm_action(action_5)
        self.assertTrue(terminate, "Failed to terminate.")  
