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
            student_interests = input("\nAI Tutor:\nCan you tell me more about yourself and what kinds of things you like to do or find interesting? I will use this to connect language and ideas to things your interested in when I teach you later:\n")
            student_slides = input("\nAI Tutor:\nCan you tell me more about how you want to be Taught? Do you learn from information or example:\n")
            student_questions = input("\nAI Tutor:\nCan you tell me more about what kind of questions you like, e.g. multiple choice, free response, \n")

            num_questions = int(input("\nAI Tutor:\nHow many questions would you like to be tested on? [5-25]\n"))
            concept_list = output["question"].split("[SEP]")
            data["list_concepts"] = concept_list
            data["student_interests"] = student_interests
            data['student_slides'] = student_slides
            data['student_questions'] = student_questions
            data["num_questions"] = num_questions
            print(concept_list)
        else: question = output["question"]
    if state == tutor.States.GENERATION:
        output, state = tutor.step(data)
        break

print(tutor.concept_database.Concepts)
print(tutor.question_suite.Questions)