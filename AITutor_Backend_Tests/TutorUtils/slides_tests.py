import unittest
from AITutor_Backend.src.TutorUtils.slides import SlidePlan, Slide, SlidePlanner, Purpose, Concept, ConceptDatabase

class SlidePlanTests(unittest.TestCase):
    def setUp(self):
        # Setup Concept Database for testing
        self.concept_db = ConceptDatabase("Concept 1", "", False)
        self.concept_db.Concepts.append(Concept("Concept 1", "Definition 1"))
        self.concept_db.Concepts.append(Concept("Concept 2", "Definition 2"))

    def test_create_slideplan_from_valid_json(self):
        llm_output = """```json{"title": "Intro to AI", "purpose": 0, "purpose_statement": "Introducing basic AI concepts", "concepts": ["Concept 1", "Concept 2"]}```"""
        slideplan = SlidePlan.create_slideplan_from_JSON(llm_output, self.concept_db)
        self.assertIsNotNone(slideplan, "SlidePlan creation from JSON should be successful")
        self.assertEqual(slideplan.title, "Intro to AI", "Error parsing LLM output for title")
        self.assertEqual(slideplan.purpose, Purpose.Introductory, "Error parsing LLM output for purpose")
        self.assertEqual(slideplan.purpose_statement, "Introducing basic AI concepts", "Error parsing LLM output for purpose statement")
        self.assertEqual(len(slideplan.concepts), 2, "Error parsing LLM output for concepts")

    def test_create_slideplan_from_invalid_json(self):
        llm_output = """```json{"title": "Invalid Slide", "purpose": "NotAnEnum", "purpose_statement": "Invalid purpose"}```"""
        with self.assertRaises(ValueError, msg="Should raise an error due to invalid JSON format"):
            SlidePlan.create_slideplan_from_JSON(llm_output, self.concept_db)

    def test_create_slideplan_missing_title(self):
        llm_output = """```json{"purpose": 0, "purpose_statement": "Missing title", "concepts": ["Concept 1"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to missing title"):
            SlidePlan.create_slideplan_from_JSON(llm_output, self.concept_db)

    def test_create_slideplan_with_unrecognized_concept(self):
        llm_output = """```json{"title": "Some Slide", "purpose": 1, "purpose_statement": "With unrecognized concept", "concepts": ["Unknown Concept"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to unrecognized concept"):
            SlidePlan.create_slideplan_from_JSON(llm_output, self.concept_db)