from AITutor_Backend.src.TutorUtils.prompts import *
notebank = NoteBank()
chat_history = ChatHistory()
prompter = Prompter("AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/question_prompt", "AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/notebank_prompt","AITutor_Backend/src/TutorUtils/Prompts/PromptingPhase/prompt_plan_prompt", notebank, chat_history)
question = "How can I help you today?"
while True:
    user_input = input(f"\nAI Tutor:\n{question}\n\nStudent:\n")
    prompt, terminate = prompter.perform_tutor(user_input)
    if terminate: break
    question = prompt._data

print('Terminated the session.')
print(f"Notebank:\n{notebank.env_string()}")
