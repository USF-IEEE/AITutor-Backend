from AITutor_Backend.src.TutorUtils.prompts import *
from AITutor_Backend.src.tutor_env import TutorEnv

tldr = '''Regular Expressions, Text Normalization, Edit Distance User: I am unhappy. ELIZA: DO YOU THINK COMING HERE WILL HELP YOU NOT TO BE UNHAPPY User: I need some help, that much seems certain. ELIZA: WHAT WOULD IT MEAN TO YOU IF YOU GOT SOME HELP User: Perhaps I could learn to get along with my mother. ELIZA: TELL ME MORE ABOUT YOUR FAMILY User: My mother takes care of me. ELIZA: WHO ELSE IN YOU FAMILY TAKES CARE OF YOU User: My father. ELIZA: YOUR FATHER User: You are like my father in some ways. Weizenbaum (1966) The dialogue above is from ELIZA, an early natural language processing system that could carry on a limited conversation with a user by imitating the responses of a Rogerian psychotherapist (Weizenbaum, 1966). ELIZA is a surprisingly simple program that uses pattern matching to recognize phrases like “I need X” and translate them into suitable outputs like “What would it mean to you if you got X?”. This simple technique succeeds in this domain because ELIZA doesn’t actually need to know anything to mimic a Rogerian psychotherapist. As Weizenbaum notes, this is one of the few dialogue genres where listeners can act as if they know nothing of the world. ELIZA’s mimicry of human conversation was remarkably successful: many people who interacted with ELIZA came to believe that it really understood them and their problems, many continued to believe in ELIZA’s abilities even after the program’s operation was explained to them (Weizenbaum, 1976), and even today such chatbots are a fun diversion. Of course modern conversational agents are much more than a diversion; they can answer questions, book flights, or find restaurants, functions for which they rely on a much more sophisticated understanding of the user’s intent, as we will see in Chapter 15. Nonetheless, the simple pattern-based methods that powered ELIZA and other chatbots play a crucial role in natural language processing. We’ll begin with the most important tool for describing text patterns: the regular expression. Regular expressions can be used to specify strings we might want to extract from a document, from transforming “I need X” in ELIZA above, to defining strings like $199 or $24.99 for extracting tables of prices from a document. We’ll then turn to a set of tasks collectively called text normalization, in which regular expressions play an important part. Normalizing text means converting it to a more convenient, standard form. For example, most of what we are going to do with language relies on first separating out or tokenizing words from running text, the task of tokenization. English words are often separated from each other by whitespace, but whitespace is not always sufficient. New York and rock ’n’ roll are sometimes treated as large words despite the fact that they contain spaces, while sometimes we’ll need to separate I’m into the two words I and am. For processing tweets or texts we’ll need to tokenize emoticons like :) or hashtags like #nlproc. Some languages, like Japanese, don’t have spaces between words, so word tokeniza- tion becomes more difficult. Another part of text normalization is lemmatization, the task of determining that two words have the same root, despite their surface differences. For example, the words sang, sung, and sings are forms of the verb sing. The word sing is the common lemma of these words, and a lemmatizer maps from all of these to sing. Lemmatization is essential for processing morphologically complex languages like Arabic. Stemming refers to a simpler version of lemmatization in which we mainly just strip suffixes from the end of the word. Text normalization also includes sen- tence segmentation: breaking up a text into individual sentences, using cues like periods or exclamation points. Finally, we’ll need to compare words and other strings. We’ll introduce a metric called edit distance that measures how similar two strings are based on the number of edits (insertions, deletions, substitutions) it takes to change one string into the other. Edit distance is an algorithm with applications throughout language process- ing, from spelling correction to speech recognition to coreference resolution.   Summary This chapter introduced a fundamental tool in language processing, the regular ex- pression, and showed how to perform basic text normalization tasks including word segmentation and normalization, sentence segmentation, and stemming. We also introduced the important minimum edit distance algorithm for comparing strings. Here’s a summary of the main points we covered about these ideas: • The regular expression language is a powerful tool for pattern-matching. • Basic operations in regular expressions include concatenation of symbols, disjunction of symbols ([], |, and .), counters (*, +, and {n,m}), anchors (ˆ, $) and precedence operators ((,)). • Word tokenization and normalization are generally done by cascades of simple regular expression substitutions or finite automata. • The Porter algorithm is a simple and efficient way to do stemming, stripping off affixes. It does not have high accuracy but may be useful for some tasks. • The minimum edit distance between two strings is the minimum number of operations it takes to edit one into the other. Minimum edit distance can be computed by dynamic programming, which also results in an alignment of the two strings.'''

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

data["user_prompt"] = "I want you to help me learn about a chapter in Natural Language Processing titled: Regular Expressions, Text Normalization, Edit Distance. I have no prior knowledge in Regular expressions, text normalization or edit distance. I am a computer science student taking a nlp class. The introduction to my chapter and summary is the following: " + tldr
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
            data["student_slides"] = student_slides
            data["student_questions"] = student_questions
            data["num_questions"] = num_questions
            print(concept_list)
        else: question = output["question"]
    if state == tutor.States.GENERATION:
        output, state = tutor.step(data)
        break

print(tutor.concept_database.Concepts)
print(tutor.question_suite.Questions)