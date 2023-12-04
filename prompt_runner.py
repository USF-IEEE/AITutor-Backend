from AITutor_Backend.src.TutorUtils.prompts import *
from AITutor_Backend.src.tutor_env import TutorEnv

tldr = '''Derivatives, Differentiation Rules, Applications User: I am struggling with calculus. ELIZA: DO YOU THINK LEARNING MORE ABOUT CALCULUS WILL HELP YOU WITH YOUR STRUGGLE? User: I need some help with derivatives, that much seems certain. ELIZA: WHAT WOULD IT MEAN TO YOU IF YOU UNDERSTOOD DERIVATIVES BETTER? User: Perhaps I could perform better in my calculus class. ELIZA: TELL ME MORE ABOUT YOUR STUDIES. User: I'm trying to understand the basic concepts of derivatives. ELIZA: WHAT SPECIFIC CONCEPTS IN DERIVATIVES ARE YOU STRUGGLING WITH? User: Things like the product and quotient rules. ELIZA: THE PRODUCT AND QUOTIENT RULES IN CALCULUS. User: Yes, and also applications like related rates. Weizenbaum (1966) The dialogue above is an adaptation of ELIZA, a natural language processing system, to illustrate the learning process of calculus concepts like derivatives. ELIZA, in this context, uses pattern matching to recognize phrases like “I need help with X” and translates them into prompts that encourage further exploration of the topic, such as “What would it mean to you if you understood X better?”. This technique aids in educational domains because the learner does not necessarily need to have deep prior knowledge. As Weizenbaum notes, in some dialogue genres, like education or therapy, listeners (or in this case, learners) can act as if they are exploring a topic anew. ELIZA’s adaptation to calculus learning, particularly in understanding derivatives, is remarkably effective: students can engage in a simulated conversation that helps reinforce their understanding and encourages them to explore topics like differentiation rules, special function derivatives, and practical applications. Today, educational chatbots can go beyond simple diversions; they can offer guided explanations, solve complex problems, or illustrate examples in calculus, functions for which they rely on a more sophisticated understanding of the student's needs and questions. Nonetheless, the simple pattern-based methods that powered ELIZA are crucial in educational technology. We’ll begin with the most essential tool for understanding calculus concepts: the basic definition of a derivative. This includes understanding limit definitions, differentiation rules (like the product and quotient rules), and applications in real-world problems like related rates. We’ll then turn to advanced topics like implicit differentiation and higher order derivatives, essential for a deeper understanding of calculus. Summary This chapter introduced fundamental tools in calculus learning, focusing on the concept of derivatives, and showed how to tackle basic and advanced topics in this area. Here’s a summary of the main points we covered about these ideas: • Understanding derivatives involves grasping basic concepts like limit definitions and differentiation rules. • Advanced operations in calculus include the product and quotient rules, chain rule, and implicit differentiation. • Real-world applications of derivatives are crucial for understanding their practical use, such as in related rates and graphical analysis. • Higher order derivatives and logarithmic differentiation are more complex topics that build on the basic understanding of derivatives.'''

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

data["user_prompt"] = "I want you to help me learn about a chapter in Calculus I titled: Derivatives,  The Definition of Derivates , Interpretation of the Derivative  Differentiation Formulas , Product and Quotient Rule ,  Derivatives of Trig Functions, Derivatives of Exponential and Logarithm Functions, Derivatives of Hyperbolic Functions, Chain Rule , Implicit Differentiation, Related Rates, Higher Order Derivatives, Logarithmic Differentiation . I have no prior knowledge Derivatives,  The Definition of Derivates , Interpretation of the Derivative  Differentiation Formulas , Product and Quotient Rule ,  Derivatives of Trig Functions, Derivatives of Exponential and Logarithm Functions, Derivatives of Hyperbolic Functions, Chain Rule , Implicit Differentiation, Related Rates, Higher Order Derivatives, Logarithmic Differentiation. I am a college student taking a calculus class. " + tldr
output, state = tutor.step(data)
question = output["question"]
if state == TutorEnv.States.GENERATION:
            student_interests = input("\nAI Tutor:\nCan you tell me more about yourself and what kinds of things you like to do or find interesting? I will use this to connect language and ideas to things your interested in when I teach you later:\n")
            student_slides = input("\nAI Tutor:\nCan you tell me more about how you want to be Taught? Do you learn from information or example:\n")
            student_questions = input("\nAI Tutor:\nCan you tell me more about what kind of questions you like, e.g. multiple choice, free response, \n")

            num_questions = int(input("\nAI Tutor:\nHow many questions would you like to be tested on? [5-25]\n"))
            concept_list = output["question"].split("[SEP]")
            data["list_concepts"] = concept_list
            data["student_interests"] = student_interests
            data["student_slides"] = student_slides
            data["student_questions"] = student_questions
            data["num_questions"] = num_questions
            print(concept_list)
            
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
            data["num_questions"] = num_questions
            print(concept_list)
        else: question = output["question"]
    if state == tutor.States.GENERATION:
        output, state = tutor.step(data)
        break

print(tutor.concept_database.Concepts)
print(tutor.question_suite.Questions)