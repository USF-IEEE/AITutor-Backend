from django.db import models
from AITutor_Backend.src.tutor_env import TutorEnv
from AITutor_Backend.src.TutorUtils.concepts import ConceptDatabase
# from AITutor_Backend.src.TutorUtils.prompts import Prompter
import uuid
from asgiref.sync import sync_to_async, async_to_sync

class ConceptDatabaseModel(models.Model):
    main_concept = models.CharField(max_length=200)
    
class ConceptModel(models.Model):
    concept_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    definition = models.TextField()
    latex = models.TextField()
    concept_database = models.ManyToManyField(ConceptDatabaseModel, related_name='concepts')

class NotebankModel(models.Model):
    notes = models.TextField()  # Assuming 'VARCHAR[n]' means text field

class ChatHistoryModel(models.Model):
    chat = models.TextField()  # Assuming 'VARCHAR[n]' means text field
  
class TutorEnvModel(models.Model):
    notebank = models.OneToOneField('NotebankModel', on_delete=models.CASCADE)
    chat_history = models.OneToOneField('ChatHistoryModel', on_delete=models.CASCADE)
    concept_database = models.ForeignKey('ConceptDatabaseModel', on_delete=models.SET_NULL, null=True, blank=True)
    curr_state = models.SmallIntegerField()

class SessionModel(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tutor = models.ForeignKey('TutorEnvModel', on_delete=models.CASCADE, related_name='sessions')

    
class DatabaseManager:
    def __init__(self, session_id):
        self.__session_id = session_id
        # Load the session with the given session ID
        self.session = SessionModel.objects.get(session_id=self.__session_id)
        self.tutor_env_model = self.session.tutor
        self.concept_database = None
    
    @staticmethod
    def create_tutor_session():
        """Returns tutor_environment_model
        """
        notebank = NotebankModel.objects.create(notes="")
        chat_history = ChatHistoryModel.objects.create(chat="")
        tutor_env_model = TutorEnvModel.objects.create(
            notebank=notebank,
            chat_history=chat_history,
            curr_state=0,
        )
        session = SessionModel.objects.create(tutor=tutor_env_model)
        tutor_env_model.save()
        session.save()
        notebank.save()
        chat_history.save()
        db_manager = DatabaseManager(session.session_id)
        return session.session_id, db_manager

    def load_tutor_env(self):
        # Load Chat History:
        chat_history_state = self.tutor_env_model.chat_history.chat
        
        # Load the Notebank:
        notebank_state = self.tutor_env_model.notebank.notes
        
        # Loads TutorEnv:
        self.tutor_env = TutorEnv.from_sql(self.tutor_env_model.curr_state, notebank_state, chat_history_state)
        
        # Load the ConceptDatabase associated with the TutorEnv:
        self.concept_database_model = self.tutor_env_model.concept_database
        if self.concept_database_model:
            self.main_concept = self.concept_database_model.main_concept
            concept_data = []
            
            # Load the concepts associated with the ConceptDatabase:
            for concept in self.concept_database_model.concepts.all():
                concept_data.append([concept.name, concept.definition, concept.latex])

            # Recreate the ConceptDatabase object from the loaded data:
            self.concept_database = ConceptDatabase.from_sql(self.main_concept, self.tutor_env.notebank.env_string(),concept_data)
        
        # Load in Time-Dependent Features:
        if self.concept_database_model:
            self.tutor_env.concept_database = self.concept_database
    
    def process_tutor_env(self, user_data):
        # Perform processing:
        system_data, current_state = self.tutor_env.step(user_data)
        return system_data, current_state
    
    def save_tutor_env(self):
        # Save any changes back to the database
        # This method should mirror the structure of the load_tutor_env method
        # but instead of loading, it should update the respective models with
        # the possibly changed data from the TutorEnv Python object

        # Save Notebank:
        self.tutor_env_model.notebank.notes = self.tutor_env.notebank.to_sql()
        self.tutor_env_model.notebank.save()
        
        # Save Chat:
        self.tutor_env_model.chat_history.chat = self.tutor_env.chat_history.to_sql()
        self.tutor_env_model.chat_history.save()

        # Save Concept Model:
        if self.tutor_env.concept_database:
            main_concept, concepts = self.tutor_env.concept_database.to_sql()
            if not self.concept_database_model: # Model was created on this time-step
                self.concept_database_model = ConceptDatabaseModel(main_concept=main_concept)
                self.concept_database_model.save()
                # Link Concepts:
                concept_models = []
                for concept_data in concepts:
                    concept_id = uuid.uuid4()
                    concept_model = ConceptModel.objects.create(
                        concept_id=concept_id,
                        name=concept_data[0],
                        definition=concept_data[1],
                        latex=concept_data[2],
                    )
                    concept_models += [concept_model]
                # Link the concepts to the ConceptDatabaseModel:
                self.concept_database_model.concepts.set(concept_models)
                    
                self.tutor_env_model.concept_database = self.concept_database_model
                self.tutor_env_model.save()
            self.concept_database_model.main_concept = self.tutor_env.concept_database.main_concept
            self.concept_database_model.save()

            concept_models = []
            for concept_data in concepts:
                try:
                    # Attempt to get the concept associated with the specific ConceptDatabaseModel:
                    concept_model = ConceptModel.objects.get(
                        name=concept_data[0], 
                        concept_database=self.concept_database_model
                    )
                    # Update with any new data since you've found an existing model
                    concept_model.definition = concept_data[1]
                    concept_model.latex = concept_data[2]
                    concept_model.save()
                except ConceptModel.DoesNotExist:
                    # If it does not exist, create it and add it to the current ConceptDatabaseModel:
                    concept_model = ConceptModel.objects.create(
                        name=concept_data[0],
                        definition=concept_data[1],
                        latex=concept_data[2]
                    )
                concept_models.append(concept_model)
            # Update DB Relationships for cdm:
            self.concept_database_model.concepts.set(concept_models)
            self.tutor_env_model.concept_database = self.concept_database_model
            self.tutor_env_model.save()

            # Save the main concept
            self.concept_database_model.main_concept = main_concept
            self.concept_database_model.save()

            # Update small Parameters:
            self.tutor_env_model.curr_state = self.tutor_env.current_state
            self.tutor_env_model.save()

        