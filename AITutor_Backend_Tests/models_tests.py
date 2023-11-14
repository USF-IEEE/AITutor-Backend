from django.test import TestCase
from AITutor_Backend.models import SessionModel, TutorEnvModel, NotebankModel, ChatHistoryModel, ConceptDatabaseModel, ConceptModel, DatabaseManager
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase, Concept
import uuid

class DatabaseManagerTestCase(TestCase):
    def setUp(self):
        # Set up your test data here
        # Create instances of your models
        self.session = DatabaseManager.create_tutor_session()
        self.tutor_env_model = self.session.tutor
        
    def operations_on_database(self, db):
        # Test the load_tutor_env method
        db.load_tutor_env()
        db.tutor_env.notebank.__notes = ["Updated test notes"]
        db.tutor_env.chat_history.hear("test user input")
        db.tutor_env.chat_history.hear("test user output")
        
        # Add concept database from other test:
        cd = ConceptDatabase("", generation=False)
        c1 = Concept("Concept 1", "")
        cd.Concepts.append(c1)
        c2 = Concept.create_from_concept_string_add_to_database("Concept 2", "Concept string mapping it to <Concept>Concept 1</Concept> which is super important.", "", cd)
        
        db.tutor_env.concept_database = cd
        # Assertions to verify the state of db_monitor after loading
        self.assertIsNotNone(db.tutor_env)
        self.assertIsNot(cd, "Concept Database is none")
        # Add more assertions here based on expected state

    def test_save_tutor_env(self):
        # Test the save_tutor_env method
        
        db = DatabaseManager(session_id=self.session.session_id)

        # Modify the tutor_env object here as needed
        # ...
        self.operations_on_database(db)
        
        db.save_tutor_env()

        # Assertions to verify that changes are saved correctly
        # Fetch the updated data from the database and assert the changes
        updated_notebank = NotebankModel.objects.get(id=self.notebank.id)
        self.assertTrue("Updated test notes" in updated_notebank.notes.strip(),)
        # Add more assertions here based on expected changes

    # Add more test methods as needed
