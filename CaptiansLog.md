# Meeting [10/29/2023] Attendees: (Jonathan Koch, Fiorella Ratti)
 - Idea: Multiple Outputs: [Teaching, Guiding, Testing | Teaching & Guiding | Teaching & Testing | Guiding & Testing | Teaching, Guiding and Testing]

- Idea: Notes Bank!

Notes Bank:
 - [0]: Note 0
 - [1]: Note 1
 ...
 - [n]: Note n

Notes Operations:
    - "ADD NOTE" where note is a AI tutor note for later plan construction or even a question for helping the AI Tutor prompt the user
    - "DEL [IDX]" where index is the index of the note to be deleted in the Notes Bank


# Meeting [11/08/2023] Attendees: (Jonathan Koch, Fiorella Ratti, Kalyan Oliveira)
 - Database will keep track of Sessions:
    - Sessions will keep track of current state:
        - State will include information regarding whats being interacted with by the user (Prompting/Teaching/Guiding/Testing)
    
    - Sessions will keep track of all Generation Data:
        - Chat History
        - Concept Database
        - Slide Planner
        - Question Suite
 
 - Database design TBD

 - Generations:
    - Concepts
    - Slides
    - Questions

 - SlidePlanner:
    - Generation will have:
        - LLM Generates Slides with the following Operations:
            - APPEND(data), MODIFY(index, data), DELETE(index), INSERT(index, data)

 - User talks to front-end, front-end sends backend user_input and session_key, backend finds environment in Database and sends user input into the environment. Environment processes user input based on current state, Environment Updates and sends Current State, and Tutor Action back to front-end

 - TutorEnvironment:
    - Executor: Doing things in the environment: (environment, user input)
    - ConceptDatabase: Manager and Generator of the Concept Data Structure
    - SlidePlanner: Managing and Generating the Slide objects of the Environment
    - QuestionSuite: Managing and Generating the Question objects of the Environment 

 - Formalizing Prompt Structure:
    - Purpose Statement: Back Story + Some Call to Action information
    - Docs: What kinds of things the model can See and Interact with i.e. Tools, Actions, E.t.c.
    - Environment State: What does the Environment Look Like?
    - Call To Action: Do something using a tool in the Docs, Perform some Action which modifies a Data Structure (described in the Docs), Generate a Data Structure described in the Docs...etc...


# Meeting [11/15/2023] Attendees: (Jonathan Koch, Fiorella Ratti, Kalyan Oliveira, Juan Gomez)
 - General checkup meeting:
    - Juan: Worked on front end, request, tested post request and it worked, implemented chat with different styles depending on the user. TODO: Send request, make a loading image to wait for server response, display content for chat and content section.
    - Kalyan: Currently finishing slides prompt. TODO: Make sure that we can make ChatGPT generate the purpose first and then the contents for each slide so it has a plan to follow during generation.
    - Jonathan: Worked on database model for data structures. Created a way to load and save tutor environment per each request, create a new tutor environment and session ID. Started setting up tutor environment to process environments. TODO: Interact with the prompting system. Enable audio and file uploads.
    - Fiorella: Finished concept graph implementation. Added prompter with perform_tutor function to construct the note bank and get prompting. TODO: Finish fixing the "question_prompt" file to get questions from LLM.
