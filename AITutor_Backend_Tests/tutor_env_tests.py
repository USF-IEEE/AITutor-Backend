import unittest
from AITutor_Backend.src.tutor_env import TutorEnv
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase, Concept
from AITutor_Backend.src.TutorUtils.questions import QuestionSuite, Question
from AITutor_Backend.src.TutorUtils.slides import SlidePlanner, Slide, Purpose


class TutorEnvTests(unittest.TestCase):
    def setUp(self):
        self.tutor_env = TutorEnv()

    def test_populate_data_from_file(self):
        self.tutor_env.concept_database = ConceptDatabase("Graph Data Structure", self.tutor_env.notebank.env_string(), False)
        # # Generate Slide Planner:
        self.tutor_env.slide_planner = SlidePlanner(self.tutor_env.notebank, self.tutor_env.concept_database)
        # # Generate Question Suite:
        num_questions = 1 
        self.tutor_env.question_suite = QuestionSuite(num_questions, self.tutor_env.notebank, self.tutor_env.concept_database)
        # Call the method under test
        TutorEnv.Executor.PopulateDataFromFile(self.tutor_env)
        # Basic assertions to ensure proper loading: We dont care about the data as long as it exists
        self.assertIsNotNone(self.tutor_env.concept_database.Concepts, "Concepts should not be None")
        self.assertIsNotNone(self.tutor_env.question_suite.Questions, "Questions should not be None")
        self.assertIsNotNone(self.tutor_env.slide_planner.Slides, "Slides should not be None")

        self.assertNotEqual(len(self.tutor_env.concept_database.Concepts), 0, "Unexpected number of concepts loaded")
        self.assertNotEqual(self.tutor_env.question_suite.num_questions, 0, "Unexpected number of questions loaded")
        self.assertNotEqual(self.tutor_env.slide_planner.num_slides, 0, "Unexpected number of slides loaded")

        self.assertNotEqual(self.tutor_env.question_suite.current_obj_idx, -1, "Unexpected number of questions loaded")
        self.assertNotEqual(self.tutor_env.slide_planner.current_obj_idx, -1, "Unexpected number of slides loaded")