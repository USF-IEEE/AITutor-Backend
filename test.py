import unittest
from AITutor_Backend_Tests.TutorUtils import notebank_tests
from AITutor_Backend_Tests.TutorUtils import prompts_tests

def create_test_suite():
    test_suite = unittest.TestSuite()
    # Add Tests from Modules:
    test_suite.addTests(unittest.TestLoader().loadTestsFromModule(notebank_tests))
    test_suite.addTests(unittest.TestLoader().loadTestsFromModule(prompts_tests))
    return test_suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(create_test_suite())