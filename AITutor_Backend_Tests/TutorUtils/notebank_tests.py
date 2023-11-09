import unittest
from AITutor_Backend.src.TutorUtils.notebank import *

class NotebankTests(unittest.TestCase):
    def test_notebank_creation_and_modification(self,):
        notebank = NoteBank()

        action_1 = """
        Sure, heres an example of what a tutor may try and output:
        ```notebank
        ADD Needs more practice with differentiation.
        ADD Maybe I should present the user with different techniques of differentiation and ask them to rank their comprehension in each.
        ```

        I hope this helps you accomplish your desired outcome :)                             
        """

        action_2 = """
        Sure, heres an example of what a tutor may try and output:
        ```notebank
        DEL [1]
        ADD User seems to understand Chain Rule and basic differentiation, but struggles with divison differentiation.
        ADD Overall, user should be given help with all types of differentiation.
        ```

        I hope this helps you accomplish your desired outcome :)                             
        """
        action_3 = """
        Sure, heres an example of what a tutor may try and output:
        ```notebank
        DEL[BAD_DATA_1]
        ADD_User seems to understand Chain Rule and basic differentiation, but struggles with divison differentiation.
        ADD Overall, user should be given help with all types of differentiation.
        ```

        I hope this helps you accomplish your desired outcome :)                             
        """
        
        action_4 = """
        Sure, heres an example of what a tutor may try and output:
        ```notebank
        DEL [10]
        ```

        I hope this helps you accomplish your desired outcome :)                             
        """

        op_suc, err_msg = notebank.process_tutor_action(action_1)
        self.assertTrue( op_suc, f"Error: unsuccesful notebank parse, {err_msg}")
        self.assertTrue(notebank.size() == 2, f"Error in parsing elements. Expected: 2, Actual: {notebank.size()}")

        op_suc, err_msg = notebank.process_tutor_action(action_2)
        self.assertTrue(op_suc, f"Error: unsuccesful notebank parse, {err_msg}")
        self.assertTrue(notebank.size() == 3, f"Error in parsing elements. Expected: 2, Actual: {notebank.size()}")

        prev_size = notebank.size()
        op_suc, err_msg = notebank.process_tutor_action(action_3)
        self.assertFalse(op_suc, f"Error: failed to detect bad notebank parse.")
        self.assertEqual(notebank.size(), prev_size, f"Additional elements added during bad parsing. Expected Size: 2, Actual Size: {notebank.size()}")
        
        op_suc, err_msg = notebank.process_tutor_action(action_4)
        self.assertFalse(op_suc, "Failed to reject bad input (10) Index Out of Bounds.")     
    