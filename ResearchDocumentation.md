# LMaAiT-BE: Large Language Models as Actors in Text-Based Environments

**Authors:** 
- Jonathan Koch <jkoch21@usf.edu>,  University of South Florida
- Fiorella Ratti Tamayo <frattitamayo@usf.edu>,  University of South Florida
- Juan Gomez <juangomez@usf.edu>, University of South Florida

## Abstract

With the advancements of Large Language Models in generative text, problem solving, and situational awareness, we can observe many emergent properties in responses produced via the prompting of a system. Additionally, we can speculate that with the power of LLM’s current problem-solving capabilities, we can formulate an interactive text-based environment; in which the model is presented with observations and can perform actions. Based on this, we hypothesize that our system will be able to exploit the problem-solving capabilities of non-finetuned Large Language Models, and should be able harness their generative power to modify the environment enough to solve some problem in which we present it. In this paper, we will explore the “Teach-a-Bull AI Tutor” environment, and how we can leverage the power previously described to solve the problem of virtualized and automated education. Our research does not suggest any sort of conclusive structure for how education should function, moreover, we present Large Language Models as Actors in Text-Based Environments (LLMaAiT-BE) to explore its capability in our designed environment and measure its performance accordingly.

## Introduction

With the development of the Transformer architecture, Large Language Models (LLMs) have exploded in capabilities expressing many emergent properties including creative writing (i.e., Poems, essays, songs, … ), information and source recollection (source citation studies), and Chatbot deployment such as Bard developed by Google, or ChatGPT from OpenAI. Furthermore, efforts to explore and extract more capabilities have demonstrated promising results adding quality to an LLMs outputs as well as expanding the LLMs previously understood abilities. Some works related to these topics include but are not limited to -- Tree of Thought(ToT); where LLM prompts are expanded based on their interpreted quality, and Voyager: LLMs learn how to Play Minecraft, where a vanilla LLM demonstrated novel capability to perform different tasks in Minecraft. Our research expands on these ideas by formalizing a method to exploit this emergent behavior; that being Large Language Models as Actors in Text-Based Environments (LLMaAiT-BE). In our research, we hope to demonstrate a reproducible method to explore the powers of LLMs as actors and provide deeper insight into the formalization methods used to do so.

(more on next page)

## Actor Generation Content:

- **Main Concept:** A central focus/idea in which a concept graph is generated from.
- **Knowledge/"Concept Graph":** a distributed collection of Concepts which contain definitions in terms of tokens and other Concepts. In other words, a concept’s definition relates it to other concepts relevant to the “Main Concept”.
- **Slides/Presentation:** Generation of formatted slides containing relevant information which the user is trying to learn and the Tutor is using to educate.
- **Examination Questions:** Generation of relevant questions to target the concepts being taught by the Tutor.

## Metrics:

### Knowledge Graph:

1. Collect “Ground Truth” data from experts in a field.
   a. Present Expert with an experience with a student requesting guidance.
   b. Ask Expert to Identify the Main Concept, Knowledge Graph in terms of concepts and relations between concepts.
2. Convert “Ground Truth” as a Vector Embedding \( y^* \), convert System output as Vector Embedding \( y' \).
3. Measure Cosine-Similarity between the embeddings.

### Slides/Presentation:

1. Collect “Ground Truth” data from experts in a field.
   a. Collect Expert slides relevant to a particular knowledge graph, such as a Calculus lecture in “differentiation techniques”. Assert that the topic of the Lecture Slides are the same as the Concept Graph’s main concept.
2. Convert “Ground Truth” as a Vector Embedding \( y^* \), convert System output as Vector Embedding \( y' \).
3. Measure Cosine-Similarity between the embeddings.

### Question Generation:

1. Collect “Ground Truth” data from experts in a field.
   a. Collect Expert exams relevant to a particular knowledge graph, such as a Calculus exam 1 in differentiation. Assert that the topics covered on the exam are relevant to the concept graph.
2. Convert “Ground Truth” as a Vector Embedding \( y^* \), convert System output as Vector Embedding \( y' \).
3. Measure Cosine-Similarity between the embeddings.

### Observations during Research

We hypothesized prior to document generation that a LLM can exhibit cognitive ability, and here's why:
   - Algorithms depend on patterns within data
   - Komogorov Compression: consider a perfect compressor K which outputs the shortest program of 1's and 0's for computing any given input X, is able to perfectly compress all data X, s.t. for all other Compressor C on C(X):
      K(X) \leq |C(X)| + K(C) + O(1)
   From this, we can derive the following equation, such that given a perfect compressor K, a dataset X and a dataset Y, the compression of CONCAT(X, Y):
      K(X, Y) = K(X) + K(Y|X) + O(log(K(X|Y)))
   such that, for any perfect compression K(X, Y), K will use the program K(X) to generate the program for Y. In a discussion of the Simons Institute, Ilya Sutskaver states the following: "First, “generate” X, then “use” X to generate Y, and this can’t be too different from generating the two datasets jointly".

   - NTP is Compression, i.e. MLE is a Compression task which language models were optimized on.
   - There are a 1-1 Correspondence between Compressors and Predictors: 
   - Ilya mentions that GPTs are optimized over an infinite space of programs using Stochastic Gradient Descent for compressing random documents on the internet, essentially the task of K(X, Y). 
   - This means that given any document D, GPT is the the theoretical best program for compressing D that we can find using SGD, given the Maximum Likelyhood Estimation Loss being optimized. This allows us to do some fairly interesting things, such as sampling a Probability distrobution P for W given a partially completed Document D'. 
   - Finetuning of Large Language Models for Chat-Assistants and Q/A oracles has proven to demonstrate that IQ ratings will increase the longer you do fine-tuning on high quality data; i.e, use Next Token Prediction to answer questions and use language in an Agent fashion can be proven to be effective just through the task of compression. 

- Cognitive Processes: 
   - We are implying that a cognitive process is an algorithmic-like pattern matching and decision-making problem which is not necessarily easy to develop a logical algorithm (typed-program) for without the utilization of a world model
   - GPT exibits algorithmic-like pattern matching and decision making:
   Generative Agents: Interactive Simulacra of Human Behavior
      - Coordination and Event Planning
      - Novel Agent Architecture
      - Memory and Retrieval 
      - Reflection
      - Planning and Reaction
      - Dialogue Generation
   
   https://www.arxiv-vanity.com/papers/2304.03442/
   - Voyager: Minecraft GPT-4 Agent; demonstrates cognitive ability in Planning, execution, and error correcting. Exhibits Continuous Learning and Adaption, Generalization and Novel Problem-Solving, Autonomous Decision Making, Zero-Shot Generalization on unseen tasks, 

   Mind meets machine: Unravelling GPT-4’s cognitive psychology 
      - Common Sense Reasoning
      - Language Processing and Creativity
      - Analogical Reasoning
      - Integrating Various Cognitive Skills

   - We propose we can simplify the cognitive abilities into the following cognitive processes:
   
   - Planning, also posit as information generation, provided with information related to the environment, create a plan for:
      - filling out a Data Structure with relevant information based on the current state of the environment
      - Memory and Planning modules used for future reference in specific states
      - Performing Actions which will modify the current state of the environment
      - Generating informational Context around a stimulus

   - Translation, translate a Natural Language plan into a JSON Object / Data Structure usable in the environment/program.
   - Discrimination, based on the environment state (ie. current generation state, current generation action, ...) discriminate:
      - Is the current action good? (i.e. does this generation pass criteria)
      - Is the current state optimal? (i.e. is this state a termination state)
      - What information is relevant for future states? (i.e. Memory/selective information passing)
I think therefore I am" <- include in paper as a side link

- I have done my own research on why this may be; "
From: The Role of Language in Intelligence
Daniel C. Dennett

- "... our brains are in effect joined together into a single cognitive system that dwarfs all others. They are joined by one of the innovations that has invaded our brains and no others: language."
- "permits our hypotheses to die in our stead."
   - Language is a complex multi-dimensional graph; we use language to form words which we compound into ideas which we use to relate to other ideas. https://www.nature.com/articles/s41599-022-01089-5/figures/5
   - These ideas relate the world of the Subjective and the world of the Objective.
   - Bad (token) predictions are optimized by good predictions. To make a good prediction, given that our model has not memorized our training data:
      - The model must extract the patterns (to some degree) of the multi-dimensional graph of language in order to predict the next token
      - This means that for unorganized or complex random internet data, our model has to be able to abstract the pattern of the data on the fly; meaning it must generalize to some degree
      - Many have speculated the expressive power of Deep Neural Networks, as a well-trained (quality and large amounts of training data) and a deep neural network will be able to perform arbitrary computation on the patterns expressed by the input data
      E.g. when we are coding there are many patterns we exhibit: 
         - indentation
         - balanced tokens "[]", "{}", "()", 
         - punctuation: semicolons, commas, ecetera
      
### Why may this be?

Model Size: research from Google, Deepmind and Stanford found that many of these emergent properties exist with bigger models; performance on cognitive tasks increased based on model size, Published in Transactions on Machine Learning Research (08/2022)
Emergent Abilities of Large Language Models (https://arxiv.org/pdf/2206.07682.pdf).

We use GPT-4 for Planning Tasks, harder Translation Tasks, and Discrimination Tasks: Speculating over 1 Trillion Parameters
We Use GPT-3.5-turbo-16k for simple planning tasks, and most translation tasks. 

We focus on Document Generation. Our research incorporates Agent Interaction, Planning and Memory Modules, Common Sense Reasoning, Conversational 

Cognitive Abilities are crucial to our document generation;
As the software engineers, we can "glue" programs and cognitive processes together; Planning to Discrimination, Planning to Translation to Discrimination, Planning to Translation, ecetera

For Example, take the Cognitive Process of Generating a Slide:
- While not Termination State:
   - Plan What the Next Slide will be About, i.e What is the Title, what is its Purpose, and What Information is it going to be used to display?
   - Translate this Plan into a JSON Object for our program
   - Discriminate whether or not the Current state, i.e. the set of Slide Plans already discovered, is a termination state; i.e.  acceptable to teach the Student
- For Each Slide Plan SP in the Slide Plan Set:
   - Generate the Slide's Context, i.e. the informational context, academic context and relevant information surrounding the chosen topic and purpose from the plan
   - Using the Slide's Context, parse and translate it into a Slide's Content JSON Object
   - Using the Slide's Context, parse and translate  it into a Slide's Presentation JSON Object 

With this, we can exploit a state-based system to perform our cognitive processes which will in turn lead to our document generations.

- Agent Ability: GPT-3.5-turbo performed poorly at first on many agent taks, while GPT-4 was able to fulfill it's role almost in every situation without struggling to maneuver the environments correctly.

- Prompting: Enabling the MDP was not the challenging part, however getting the model to terminate was challenging. We found that the model likes the idea of continuing the process for as long as possible. 

Consider the # of API Calls / # Process Iterations 

- With strictly GPT-3.5-turbo you end up making more API Calls due to failures

TODO: Perform metric comparison

- Cognitive Processes over Cognitive Tasks:
   - Translation performs worse than Planning and Translation in generation quality and ...


 
# Online View Only of Paper: 
(https://www.overleaf.com/read/sbwnyxczkrcj#49db64)