import unittest
import os
import json
import pickle as pkl

GENERATE_DATA = bool(os.environ.get("GENERATE_TESTS", 0))

from AITutor_Backend.src.TutorUtils.slides import SlidePlan, Slide, SlidePlanner, Purpose, Concept, ConceptDatabase
from AITutor_Backend.src.TutorUtils.notebank import NoteBank

agent_ai_notes = """User expresses interest in learning about agent AI.
Main Concept: Agent AI
Student wants to learn about agent AI.
Subconcept: Introduction to Artificial Intelligence"}{"index": 4, "note": "Subconcept: Definition and Characteristics of Agents
Subconcept: Agent Architectures
Subconcept: Agent Environments
Subconcept: Agent Communication and Coordination
Subconcept: Learning Agents and Adaptive Behavior
Subconcept: Multi-Agent Systems"}
Subconcept: Intelligent Agents in Games, Robotics, and Simulation
Subconcept: Ethical Considerations and Future Trends in Agent AI
Tutor needs to gauge student's background knowledge 
in artificial intelligence and computer science.
Tutor should ask student about their specific interests in agent AI and any particular agent types or applications they want to learn 
Tutor should inquire about the student's goals in learning about agent AI.
Tutor should ask student about their preference for 
a theoretical or practical approach to learning agent AI.
Tutor should ask student about their familiarity with programming languages or tools used in AI development.
Tutor to ask student about their familiarity with programming languages and tools used in AI development.
Tutor to ask student about their specific interests 
in agent AI and any particular agent types or applications they want to learn about
Tutor to ask student about their goals in learning about agent AI.
Tutor to ask student about their preference for a theoretical or practical approach to learning agent AI.
Tutor should gauge student's current understanding of agent AI concepts to create a targeted learning plan.
Tutor should document their responses and preferences in the Notebank for future reference.
"""

regex_notes = """User expresses interest in learning about regular expressions.
Main Concept: Regular Expressions
Student wants to learn about regular expressions.
Subconcept: Introduction to Regular Expressions
Subconcept: Text Normalization
Subconcept: Expression Patterns
Subconcept: Concatenation
Subconcept: Disjunction
Subconcept: Range
Subconcept: Kleene Star and Plus
Subconcept: Anchors
Subconcept: Counters
Subconcept: Precedence
Subconcept: Substitution
Subconcept: Lookahead Assertions
Student has limited prior knowledge of regex concepts in string manipulation and pattern matching.
Student wants to becom proficient in regular expressions.
Student Interest Statement: I like bird watching, I have a nest in my backyard with a camera that tracks birds over time, its so cute.
Student Slides Statement: I learn by example, the more examples the better.
Student Questions Statement: I would like to tackle programming questions and multiple choice questions.
"""


# Defining the concepts in the subtree
cd = ConceptDatabase("Regular Expression", "", generation=False)
regular_expression = Concept.create_from_concept_string_add_to_database(
    "Regular Expression",
    "A sequence of characters that form a search pattern, often used for string matching and manipulation.",
    "", cd
)

text_normalization = Concept.create_from_concept_string_add_to_database(
    "Text normalization",
    "Process of transforming text into a more consistent format, often used in conjunction with <Concept>Regular Expression</Concept>.",
    "", cd
)

expression_patterns = Concept.create_from_concept_string_add_to_database(
    "Expression Patterns",
    "Specific patterns used within a <Concept>Regular Expression</Concept>, including Concatenation, Disjunction, etc.",    "", cd)

# Sub-concepts of Expression Patterns
concatenation = Concept.create_from_concept_string_add_to_database(
    "Concatenation",
    "A type of <Concept>Expression Pattern</Concept> where two strings are joined end-to-end.",
    "", cd
)

disjunction = Concept.create_from_concept_string_add_to_database(
    "Disjunction",
    "A type of <Concept>Expression Pattern</Concept> representing a choice between alternatives.",
    "", cd
)

range_c = Concept.create_from_concept_string_add_to_database(
    "Range",
    "A <Concept>Expression Pattern</Concept> that specifies a range of characters to match.",
    "", cd
)

kleene = Concept.create_from_concept_string_add_to_database(
    "Kleene",
    "A <Concept>Expression Pattern</Concept> indicating zero or more occurrences of the previous element.",
    "", cd
)

anchors = Concept.create_from_concept_string_add_to_database(
    "Anchors",
    "Special <Concept>Expression Patterns</Concept> that assert a position within the text.",
    "", cd
)

counters = Concept.create_from_concept_string_add_to_database(
    "Counters",
    "Quantifiers in a <Concept>Regular Expression</Concept> that specify how many times a component should occur.",
    "", cd
)

precedence = Concept.create_from_concept_string_add_to_database(
    "Precedence",
    "The order in which operations in a <Concept>Regular Expression</Concept> are carried out.",
    "", cd
)

substitution = Concept.create_from_concept_string_add_to_database(
    "Substitution",
    "Replacing text in a string that matches a <Concept>Regular Expression</Concept>.",
    "", cd
)

lookahead_assertions = Concept.create_from_concept_string_add_to_database(
    "Lookahead Assertions",
    "Conditional <Concept>Expression Patterns</Concept> in a <Concept>Regular Expression</Concept> that look ahead in the text.",
    "", cd
)

regular_expression.refs.extend([text_normalization, expression_patterns])
expression_patterns.refs.extend([concatenation, disjunction, range_c, kleene, anchors, counters, precedence, substitution, lookahead_assertions])

# Manual Testing:
# notebank = NoteBank()
# [notebank.add_note(n) for n in regex_notes.split("\n")]
# slide_planner = SlidePlanner(notebank, cd)
# # Check if the file exists
# if os.path.exists("./temp_slideplan.pkl"):
#     # Load the object from the file
#     with open("./temp_slideplan.pkl", "rb") as f:  # 'rb' mode is for reading in binary format
#         slide_plans = pkl.load(f)
#         slide_planner.SlidePlans = slide_plans
# else:
#     slide_planner.generate_slide_plan()
#     with open("./temp_slideplan.pkl", "wb") as f:  # 'wb' mode is for writing in binary format
#         pkl.dump(slide_planner.SlidePlans, f)

# slide_planner.generate_slide_deque()
# print("\n\n".join([slide.format_json() for slide in slide_planner.Slides]))

class SlidePlanTests(unittest.TestCase):
    def setUp(self):
        # Setup Concept Database for testing
        self.concept_db = ConceptDatabase("Concept 1", "", False)
        self.concept_db.Concepts.append(Concept("Concept 1", "Definition 1"))
        self.concept_db.Concepts.append(Concept("Concept 2", "Definition 2"))

    def test_generation_slides(self):
        notebank = NoteBank()
        [notebank.add_note(n) for n in regex_notes.split("\n")]
        slide_planner = SlidePlanner(notebank, cd)
        slide_planner.generate_slide_plan()
        slide_planner.generate_slide_deque()

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