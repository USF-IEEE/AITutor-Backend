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

- Prompting: Enabling the MDP was not the challenging part, however getting the model to terminate was challenging. We found that the model likes the idea of continuing the process for as long as possible. 

- Agent Ability: GPT-3.5-turbo performed poorly on many agent taks, while GPT-4 was able to fulfil it's role almost in every situation without struggling to output correctly.

- Cognitive Processes: 
   - We are implying that a cognitive process is an algorithmic-like 
GPT exhibits Mid and low-level cognitive ability with the following cognitive processes:
   - Planning, provided with information related to the environment, create a plan for filling out a Data Structure with relevant information based on the current state of the environment 
   - Translation, translate a Natural Language plan into a JSON Object / Data Structure usable in the environment/program.
   - Discrimination, based on the environment state (ie. current generation state, current generation action, ...) discriminate:
      - Is the current action good? (i.e. does this generation pass criteria)
      - Is the current state optimal? (i.e. is this state a termination state)
      - What information is relevant for future states? (i.e. Memory/selective information passing)

This is crucial to our document generation;
As the software engineers, we can "glue" cognitive processes together; Planning to Discrimination, Planning to Translation to Discrimination, Planning to Translation, ecetera

With this, we can exploit a state-based system to perform our cognitive processes which will in turn lead to our document generations. We hypothesized prior to document generation that a LLM can exhibit cognitive ability, and here's why:
   - Algorithms depend on patterns within data
   - Komogorov Compression: consider a perfect compressor K which is able to perfectly compress all data, s.t. K(X) <= Any other ... TODO 
   - NTP is Compression, i.e. we are simply maximizing the NLL of of the 

- ChatGPT will freeze occasionally when making its predictions. Essentially, this would render the generation. We have to prompt it several times for it to get better. For a student trying to learn, this process migth get frustrating. This is why chatgpt might not be an adequate resource for just learning.
