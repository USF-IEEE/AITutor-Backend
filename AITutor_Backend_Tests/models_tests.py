from django.test import TestCase
from AITutor_Backend.models import SessionModel, TutorEnvModel, NotebankModel, ChatHistoryModel, ConceptDatabaseModel, ConceptModel, QuestionSuiteModel, QuestionModel, DatabaseManager
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase, Concept
from AITutor_Backend.src.TutorUtils.questions import QuestionSuite, Question
from asgiref.sync import sync_to_async, async_to_sync
import uuid

class DatabaseManagerTestCase(TestCase):
    def setUp(self):
        pass
        # Set up new DB:
        
    def operations_on_database1(self, ):
        # Assertions to verify the state of db_monitor after loading
        self.assertIsNotNone(self.db_manager.tutor_env, "Error creating the tutorenv model")
        assert self.db_manager.tutor_env.notebank is not None, "Error creating the notebank model"
        self.db_manager.tutor_env.notebank.process_llm_action("""```json\n[{"action": "add", "note": "Updated test notes"}]```""")
        assert self.db_manager.tutor_env.chat_history is not None, "Error creating the chathistory model"
        self.db_manager.tutor_env.chat_history.hear("test user input")
        self.db_manager.tutor_env.chat_history.respond("test user output")
        
        # Add concept database from other test:
        cd = ConceptDatabase("Testing", generation=False)
        c1 = Concept("Concept 1", "")
        cd.Concepts.append(c1)
        c2 = Concept.create_from_concept_string_add_to_database("Concept 2", "Concept string mapping it to <Concept>Concept 1</Concept> which is super important.", "", cd)
        
        # Add question suite and questions
        qs = QuestionSuite(num_questions=1, Notebank=self.db_manager.tutor_env.notebank, ConceptDatabase=self.db_manager.tutor_env.concept_database)
        q1 = Question(Question.Subject.MATH, Question.Type.TEXT_ENTRY, {"data": "Sample math question"}, [c1, c2])
        qs.Questions.append(q1)
        self.db_manager.tutor_env.question_suite = qs
        self.db_manager.tutor_env.concept_database = cd
        self.assertIsNotNone(cd, "Concept Database is none")
        # Add more assertions here based on expected state

    def operations_on_database2(self, ):
        # Assertions to verify the state of db_monitor after loading
        self.assertIsNotNone(self.db_manager.tutor_env, "Error reloading the tutorenv model")
        # Test the load_tutor_env method
        assert self.db_manager.tutor_env.notebank is not None, "Error reloading the notebank model"
        self.db_manager.tutor_env.notebank.process_llm_action("""```json\n[{"action": "add", "note": "Updated my test notes again"}]```""")
        assert self.db_manager.tutor_env.chat_history is not None, "Error reloading the chathistory model"
        self.db_manager.tutor_env.chat_history.hear("test user input more")
        self.db_manager.tutor_env.chat_history.respond("test user output more")
        
        # Add concept database from other test:
        assert self.db_manager.tutor_env.concept_database is not None, "Error reloading the conceptdatabase model"
        c3 = Concept.create_from_concept_string_add_to_database("Concept 3", "Concept string mapping it to <Concept>Concept 2</Concept> which is super important.", "", self.db_manager.tutor_env.concept_database)
        # Modify question suite and add new questions
        q2 = Question(Question.Subject.CODE, Question.Type.CODE_ENTRY, {"data": "Sample coding question"}, [c3])
        self.db_manager.tutor_env.question_suite.Questions.append(q2)
        self.db_manager.tutor_env.question_suite.num_questions = 2
        self.db_manager.tutor_env.question_suite.current_obj_idx = 1 # Update param field
        # Modify current state:
        self.db_manager.tutor_env.current_state = 2
        
    def test_create_modify_save_pull_modify_save_tutor_env(self):
        ## test Create Modify Save Functionality:
        self.session_id, self.db_manager = DatabaseManager.create_tutor_session()
        self.tutor_env_model = self.db_manager.tutor_env_model
        self.db_manager.load_tutor_env()
        self.operations_on_database1()
        self.db_manager.save_tutor_env()
        # Verify that Data saved correctly:
        updated_notebank = NotebankModel.objects.get(id=self.tutor_env_model.notebank.id)
        self.assertTrue("Updated test notes" in updated_notebank.notes.strip(), "Error while saving the Notebank")
        
        updated_chat_history = ChatHistoryModel.objects.get(id=self.tutor_env_model.chat_history.id)
        self.assertTrue("test user input" in updated_chat_history.chat and "test user output" in updated_chat_history.chat, "Error while saving Chat History") 
        
        updated_concept_database = ConceptDatabaseModel.objects.get(id=self.tutor_env_model.concept_database.id)
        self.assertEqual(updated_concept_database.main_concept, "Testing", "Error while saving Concept Database.")
        
        concept_2 = ConceptModel.objects.get(name="Concept 2", concept_database=updated_concept_database)
        self.assertEqual(concept_2.name, "Concept 2", "Error while saving a Concept Model")
        
        self.assertTrue("<Concept>Concept 1</Concept>" in concept_2.definition, "Error while parsing the concept's definition")
        
        self.assertEqual(self.tutor_env_model.curr_state, 0, "Error while saving the TutorEnvModel.")
        
        # Verify that QuestionSuite and Questions saved correctly after first operation
        updated_qs = QuestionSuiteModel.objects.get(id=self.tutor_env_model.question_suite.id)
        self.assertEqual(len(updated_qs.questions.all()), 1, "Error while saving Questions in QuestionSuite")
        # Testing min on num_questions for generation
        self.assertEqual(updated_qs.num_questions, 5, "Error saving num_questions Field on QuestionSuite Model")
        self.assertEqual(updated_qs.current_obj_idx, -1, "Error saving Default current object index on QuestionSuiteModel")
        question_1 = QuestionModel.objects.get(subject=Question.Subject.MATH.value, question_suite=updated_qs)
        self.assertTrue("Concept 1" in question_1.concepts and "Concept 2" in question_1.concepts, "Error matching Concepts")
        self.assertTrue("Sample math question" in question_1.data, "Error while saving a Question Model")

        
        ## Create Modify Save Functionality works.
        
        ## Test Pull Modify Save Functionality:
        self.db_manager = DatabaseManager(self.session_id) # Use our session id
        self.tutor_env_model = self.db_manager.tutor_env_model
        self.db_manager.load_tutor_env()
        self.operations_on_database2()
        self.db_manager.save_tutor_env()
        # Verify that Data saved correctly:
        updated_notebank = NotebankModel.objects.get(id=self.tutor_env_model.notebank.id)
        self.assertTrue("Updated test notes" in updated_notebank.notes.strip() and "Updated my test notes again" in updated_notebank.notes.strip(), "Error while re-saving the Notebank")
        
        updated_chat_history = ChatHistoryModel.objects.get(id=self.tutor_env_model.chat_history.id)
        self.assertTrue("test user input" in updated_chat_history.chat and "test user output" in updated_chat_history.chat and "test user input more" in updated_chat_history.chat and "test user output more" in updated_chat_history.chat, "Error while re-saving Chat History") 
        
        updated_concept_database = ConceptDatabaseModel.objects.get(id=self.tutor_env_model.concept_database.id)
        self.assertEqual(updated_concept_database.main_concept, "Testing", "Error while saving Concept Database.")
        
        concept_3 = ConceptModel.objects.get(name="Concept 3", concept_database=updated_concept_database)
        self.assertEqual(concept_3.name, "Concept 3", "Error while saving a Concept Model")
        self.assertTrue("<Concept>Concept 2</Concept>" in concept_3.definition, "Error while parsing the concept's definition")
        
        updated_qs = QuestionSuiteModel.objects.get(id=self.tutor_env_model.question_suite.id)
        self.assertEqual(len(updated_qs.questions.all()), 2, "Error while re-saving Questions in QuestionSuite")
        self.assertEqual(updated_qs.num_questions, 2, "Error saving num_questions Field on QuestionSuite Model")
        self.assertEqual(updated_qs.current_obj_idx, 1, "Error saving updated current object index on QuestionSuiteModel")
        
        question_2 = QuestionModel.objects.get(subject=Question.Subject.CODE.value, question_suite=updated_qs)
        self.assertTrue("Concept 3" in question_2.concepts, "Error matching Concepts")
        self.assertTrue("Sample coding question" in question_2.data, "Error while re-saving a Question Model")
        self.assertEqual(self.tutor_env_model.curr_state, 2, "Error while re-saving the TutorEnvModel.")
        ## Test Pull Modify Save Functionality works.
