from AITutor_Backend.src.TutorUtils.prompts import *
from AITutor_Backend.src.tutor_env import TutorEnv

notebank = NoteBank()
chat_history = ChatHistory()
# prompter = Prompter("AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/question_prompt", "AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/notebank_prompt","AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/prompt_plan_prompt", notebank, chat_history)
tutor = TutorEnv()

question = "How can I help you today?"


{"guiding": None}
{"testing": None}
{"prompt": None}
state = tutor.States.PROMPTING

data = {}
while True:
    if state == tutor.States.PROMPTING:
        data["user_prompt"] = input(f"\nAI Tutor:\n{question}\n\nStudent:\n")
        output, state = tutor.step(data)
        if state == TutorEnv.States.GENERATION:
            concept_list = output["question"].split("[SEP]")
            data["concept_list"]
        else: question = output["question"]
    if state == tutor.States.GENERATION:
        output, state = tutor.step(data)
        break

print(tutor.concept_database.Concepts)
print(tutor.question_suite.Questions)
