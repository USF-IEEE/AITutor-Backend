# AITutor-Backend

AITutor-Backend is a part of the LMaAiT-BE (Large Language Models as Actors in Text-Based Environments) project, focusing on leveraging Large Language Models for creating interactive, text-based educational environments. This is an ongoing research project for USF IEEE AI Group. Our group is commited to developing research projects relevant to modern approaches and technologies.

Note: This application is designed to run with USF-IEEE/AITutor_Frontend. Find that repo [here](https://github.com/USF-IEEE/AITutor-Frontend).

## Authors

- Jonathan Koch <jkoch21@usf.edu>, University of South Florida
- Fiorella Ratti Tamayo <frattitamayo@usf.edu>, University of South Florida
- Juan Gomez <juangomez@usf.edu>, University of South Florida

## Setup and Installation

To set up the AITutor-Backend environment, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/USF-IEEE/AITutor-Backend
   cd AITutor-Backend
   ```

2. Set up a virtual environment (using conda or venv):
   ```
   # Example using venv
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create and migrate the database:
   ```
   python manage.py makemigrations AITutor_Backend
   ./run_migrations.sh  # On Windows use `run_migrations.bat`
   ```

## Running the Application

- To run the unit tests (GENERATION_TESTS enabled only if specified):
  ```
  GENERATION_TESTS=1 python test.py
  ```

- To start the backend server:
  ```
  DEBUG=1 python run.py
  ```

- To run the console demo:
  ```
  python prompt_runner.py
  ```

## Research Documentation

**Abstract:** The LMaAiT-BE project explores the capabilities of Large Language Models in an interactive text-based educational environment. This research investigates how these models can be utilized for automated education, leveraging their problem-solving and generative abilities.

**Introduction:** The project builds on the advancements in Transformer architecture and the emergent properties of LLMs in various domains such as creative writing, source citation, and chatbot applications.

### Components

- **Actor Generation Content:** Central focus concepts, knowledge graphs, slides/presentations, and examination questions.
- **Metrics:** Evaluation includes knowledge graph accuracy, slide/presentation relevance, and question generation quality, measured via cosine similarity of vector embeddings.

### Cognitive Processes Explored

The project delves into cognitive abilities like planning, translation, discrimination, and more, showcasing the potential of LLMs in simulating human-like cognitive processes.

### Research Notes

Discusses the underlying hypotheses and theoretical foundations, including discussions on cognitive processes, algorithmic pattern matching, and the role of language in intelligence.

### Full Paper

Access the full research paper [here](https://www.overleaf.com/read/sbwnyxczkrcj#49db64).

#### Fix with Archiv Reference ^
