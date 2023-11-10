from django.db import models

class TutorEnvModel(models.Model):
    env_id = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return f"TutorEnvironment {self.id}"

class SessionModel(models.Model):
    session_id = models.CharField(max_length=64, unique=True)
    env_id = models.ForeignKey(TutorEnvModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.session_id
