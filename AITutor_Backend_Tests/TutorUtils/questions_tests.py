import unittest
from AITutor_Backend.src.TutorUtils.questions import QuestionSuite, Question
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase, Concept
from AITutor_Backend.src.TutorUtils.notebank import NoteBank

class QuestionSuiteTests(unittest.TestCase):
    def setUp(self):
        self.notebank = NoteBank()
        self.concept_db = ConceptDatabase("Test Concept", generation=False)
        self.concept_db.Concepts.append(Concept("Test Concept 1", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 2", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 3", ""))
        self.concept_db.Concepts.append(Concept("Test Concept 4", ""))
        self.question_suite = QuestionSuite(5, self.notebank, self.concept_db)

    def test_initialization(self):
        self.assertEqual(len(self.question_suite.Questions), 0, "Initial question list should be empty")

    def test_generate_question_data(self):
        return # TODO: Integrate Generation Testing on GH Actions
        self.question_suite.generate_question_data()
        self.assertEqual(len(self.question_suite.Questions), 5, "QuestionSuite should generate specified number of questions")

    def test_env_string_format(self):
        return # TODO: Integrate Generation Testing on GH Actions
        self.question_suite.generate_question_data()
        env_string = self.question_suite.env_string()
        self.assertTrue(isinstance(env_string, str), "Environment string should be a string")

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
        

    def test_to_sql_and_from_sql(self):
        sql_data = self.question.to_sql()
        reconstructed_question = Question.from_sql(sql_data[0], sql_data[1], sql_data[2], [self.concept])
        self.assertEqual(reconstructed_question.data['data'], "Sample question", "from_sql should correctly reconstruct the question")

    def test_format_json(self):
        json_data = self.question.format_json()
        self.assertTrue(isinstance(json_data, dict), "Formatted JSON should be a dictionary")