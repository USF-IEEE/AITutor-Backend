import unittest
import os
import json

GENERATE_DATA = bool(os.environ.get("GENERATE_TESTS", 0))

from AITutor_Backend.src.TutorUtils.questions import QuestionSuite, Question
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase, Concept
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

# Concept class definition (assuming it's already defined in your environment)
# class Concept:
#     def __init__(self, name, definition):
#         self.name = name
#         self.definition = definition
#         self.refs = []

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


# Adding references (for demonstration, assuming this functionality is part of the Concept class)
regular_expression.refs.extend([text_normalization, expression_patterns])
expression_patterns.refs.extend([concatenation, disjunction, range_c, kleene, anchors, counters, precedence, substitution, lookahead_assertions])

class QuestionSuiteTests(unittest.TestCase):
    def setUp(self):
        self.notebank = NoteBank()
        self.concept_db = ConceptDatabase("Test Concept 1", generation=False)
        self.concept_db.Concepts.append(Concept("Test Concept 1", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 2", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 3", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 4", ""))
        self.question_suite = QuestionSuite(5, self.notebank, self.concept_db)

    def test_initialization(self):
        self.assertEqual(len(self.question_suite.Questions), 0, "Initial question list should be empty")

    def test_generate_question_data(self):
        if not GENERATE_DATA: return
        # return # TODO: Integrate Generation Testing on GH Actions
        notebank = NoteBank()
        [notebank.add_note(note) for note in agent_ai_notes.split("\n")]
        cd = ConceptDatabase("Agent Artificial Intelligence", notebank.env_string())
        q_suite = QuestionSuite(10, notebank, cd)
        q_suite.generate_question_data()
        self.assertEqual(len(self.question_suite.Questions), 10, "QuestionSuite should generate specified number of questions")

    def test_generate_and_env_string_format(self):
        if not GENERATE_DATA: return         
        q_suite = QuestionSuite(5, self.notebank, cd)
        q_suite.generate_question_data()
        env_string = q_suite.env_string()
        self.assertIsInstance(env_string, str, "Environment string should be a string")

    def test_to_sql_and_from_sql(self):
        q_suite = QuestionSuite(3, self.notebank, self.concept_db)
        q_suite.Questions = [Question(i, i, {"test": 42, "test2": "this is test data"}, [self.concept_db.get_concept(f"Test Concept {i+1}")]) for i in range(4)]
        sql_data = q_suite.to_sql()
        new_question_suite = QuestionSuite.from_sql(sql_data[0], sql_data[1], sql_data[2], self.notebank, self.concept_db)
        self.assertEqual(len(new_question_suite.Questions), 4, "from_sql should correctly reconstruct the question suite")
        for i in range(4):
            self.assertEqual(i, q_suite.Questions[i].subject, "Error in saving SQL Data, Question Subject's failed to permeate.")
            self.assertEqual(i, q_suite.Questions[i].type, "Error in saving SQL Data, Question Type's failed to permeate.")
            self.assertTrue("test" in q_suite.Questions[i].data and 42 == q_suite.Questions[i].data["test"]), "Invalid SQL save for Qustion."
            self.assertTrue("test2" in q_suite.Questions[i].data and "this is test data" == q_suite.Questions[i].data["test2"]), "Invalid SQL save for Qustion."
            self.assertEqual(q_suite.Questions[i].concepts[0].name, f"Test Concept {i+1}","Failed to find names Equal, check CDB or SQL Concept Name storage.")
            

class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.concept_db = ConceptDatabase("Test Concept 1", generation=False)
        self.concept = Concept("Test Concept 1", "")
        self.concept_db.Concepts.append(self.concept)
        self.question_data = {
            "subject": 0,
            "type": 1,
            "data": "Sample question",
            "entry1": "abcd",
            "entry2": "efg",
            "correct_entry": "entry2",
            "concepts": ["Test Concept 1"]
        }
        self.question = Question(Question.Subject.MATH, Question.Type.MULTIPLE_CHOICE, self.question_data, [self.concept])

    def test_create_question_from_json(self):
        # Math Multiple Choice:
        json_output = """```json{"subject": 0, "type": 1, "data": "some fun question about derivitives?", "entry1":"a", "entry2": "b", "correct_entry": "entry1", "latex_code": "\\frac{d}{dx}", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful")
        self.assertEqual( question.data["data"], "some fun question about derivitives?", "Error parsing LLM output for question data parameter.")
        self.assertEqual( question.data["entry2"], "b", "Error parsing LLM output for entry parameter.")
        
        # Literature Text Entry:
        json_output = """```json{"subject": 2, "type": 0, "data": "some fun question about star wars?","reading_passage":"A long long time ago, there was a galaxy far far away", "rubric": "[5 points] student exhibits a love for star wars", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful")
        self.assertEqual( question.data["reading_passage"], "A long long time ago, there was a galaxy far far away", "Error parsing LLM output for question data parameter.")
        self.assertEqual( question.data["rubric"], "[5 points] student exhibits a love for star wars", "Error parsing LLM output for rubric parameter.")
        # Coding Question:
        json_output = """```json{"subject": 1, "type": 3, "data": "some fun question about BFS?", "test_cases_script":"print(\'Hello World\')", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful")
        self.assertEqual( question.data["data"], "some fun question about BFS?", "Error parsing LLM output for question data parameter.")
        self.assertEqual( question.data["test_cases_script"], "print(\'Hello World\')", "Error parsing LLM output for test_cases_script parameter.")
        
        # Calculation Question:
        json_output = """```json{"subject": 0, "type": 2, "data": "some math thing add 5 and 7.", "calculation_script":"print(5+7)", "latex_code": "5+7", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful")
        self.assertEqual(question.data["data"], "some math thing add 5 and 7.", "Error parsing LLM output for question data parameter.")
        self.assertEqual(question.data["calculation_script"], "print(5+7)", "Error parsing LLM output for calculation_script parameter.")
        
        # Test Case: Math Multiple Choice with Incorrect Format
        json_output = """```json{"subject": 0, "type": 1, "data": "A math question?", "latex_code": "f(x)", "entry1":"x", "correct_entry": "entry1", "concepts": ["Test Concept 1"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to missing entry2"):
            Question.create_question_from_JSON(json_output, self.concept_db)

        # Test Case: Literature Text Entry with Missing Passage
        json_output = """```json{"subject": 2, "type": 0, "data": "Question about a novel?", "rubric": "[5 points] detailed analysis", "concepts": ["Test Concept 1"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to missing reading passage"):
            Question.create_question_from_JSON(json_output, self.concept_db)

        # Test Case: Code Question with Missing Test Case Script
        json_output = """```json{"subject": 1, "type": 3, "data": "Write a function in Python.", "concepts": ["Test Concept 1"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to missing test_cases_script"):
            Question.create_question_from_JSON(json_output, self.concept_db)

        # Test Case: Calculation Question without Calculation Script
        json_output = """```json{"subject": 0, "type": 2, "data": "Calculate 5 * 5.", "latex_code": "5 \\times 5", "concepts": ["Test Concept 1"]}```"""
        with self.assertRaises(AssertionError, msg="Should raise an error due to missing calculation_script"):
            Question.create_question_from_JSON(json_output, self.concept_db)

        # Test Case: Incorrect JSON Format
        json_output = """```json"subject": 1, "type": 2, "data": "Syntax Error.", "concepts": ["Test Concept 1"]}```"""
        with self.assertRaises(ValueError, msg="Should raise an error due to incorrect JSON format"):
            Question.create_question_from_JSON(json_output, self.concept_db)

        # Test Case: Valid Conceptual Question (Multiple Choice)
        json_output = """```json{"subject": 3, "type": 1, "data": "Conceptual question?", "entry1": "Option A", "entry2": "Option B", "correct_entry": "entry1", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful for a valid conceptual question")
        self.assertEqual(question.data["data"], "Conceptual question?", "Error parsing LLM output for question data parameter.")
        self.assertEqual(question.data["correct_entry"], "entry1", "Error parsing LLM output for correct_entry parameter.")

        # Test Case: Literature Multiple Choice Question
        json_output = """```json{"subject": 2, "type": 1, "data": "Question about a poem?", "entry1": "Option A", "entry2": "Option B", "correct_entry": "entry1", "reading_passage": "Some poem text here", "concepts": ["Test Concept 1"]}```"""
        question = Question.create_question_from_JSON(json_output, self.concept_db)
        self.assertIsNotNone(question, "Question creation from JSON should be successful for a literature multiple choice question")
        self.assertEqual(question.data["reading_passage"], "Some poem text here", "Error parsing LLM output for reading_passage parameter.")



    def test_to_sql_and_from_sql(self):
        sql_data = self.question.to_sql()
        reconstructed_question = Question.from_sql(sql_data[0], sql_data[1], sql_data[2], [self.concept])
        self.assertEqual(reconstructed_question.data['data'], "Sample question", "from_sql should correctly reconstruct the question")

    def test_format_json(self):
        json_data = self.question.format_json()
        self.assertTrue(isinstance(json_data, dict), "Formatted JSON should be a dictionary")