import unittest
from AITutor_Backend.src.TutorUtils.concepts import *

class NotebankTests(unittest.TestCase):
    def test_concept_graph(self,):
        cd = ConceptDatabase("", generation=False)
        c1 = Concept("Concept 1", "")
        cd.Concepts.append(c1)
        c2 = Concept.create_from_concept_string_add_to_database("Concept 2", "Concept string mapping it to <Concept>Concept 1</Concept> which is super important.", "", cd)

        assert c1 in c2.refs, "Did not map correctly."
        assert c1 in c2.definition, "Did not map correctly"
    
    def test_generate_concept_graph(self,):
        tutor_plan = """{"Notebank": [{"index": 0, "note": "User expresses interest in learning about agent AI."}
{"index": 1, "note": "Main Concept: Agent AI"}
{"index": 2, "note": "Student wants to learn about agent AI."}
{"index": 3, "note": "Subconcept: Introduction to Artificial Intelligence"}{"index": 4, "note": "Subconcept: Definition and Characteristics of Agents"}
{"index": 5, "note": "Subconcept: Agent Architectures"}
{"index": 6, "note": "Subconcept: Agent Environments"}
{"index": 7, "note": "Subconcept: Agent Communication and Coordination"}   
{"index": 8, "note": "Subconcept: Learning Agents and Adaptive Behavior"}  
{"index": 9, "note": "Subconcept: Multi-Agent Systems"}
{"index": 10, "note": "Subconcept: Intelligent Agents in Games, Robotics, and Simulation"}
{"index": 11, "note": "Subconcept: Ethical Considerations and Future Trends in Agent AI"}
{"index": 12, "note": "Tutor needs to gauge student's background knowledge 
in artificial intelligence and computer science."}
{"index": 13, "note": "Tutor should ask student about their specific interests in agent AI and any particular agent types or applications they want to learn about."}
{"index": 14, "note": "Tutor should inquire about the student's goals in learning about agent AI."}
{"index": 15, "note": "Tutor should ask student about their preference for 
a theoretical or practical approach to learning agent AI."}
{"index": 16, "note": "Tutor should ask student about their familiarity with programming languages or tools used in AI development."}
{"index": 17, "note": "Tutor to ask student about their familiarity with programming languages and tools used in AI development."}
{"index": 18, "note": "Tutor to ask student about their specific interests 
in agent AI and any particular agent types or applications they want to learn about."}
{"index": 19, "note": "Tutor to ask student about their goals in learning about agent AI."}
{"index": 20, "note": "Tutor to ask student about their preference for a theoretical or practical approach to learning agent AI."}
{"index": 21, "note": "Tutor should gauge student's current understanding of agent AI concepts to create a targeted learning plan."}
{"index": 22, "note": "Tutor should document their responses and preferences in the Notebank for future reference."}]}"""
        cd = ConceptDatabase("Agent Artificial Intelligence", tutor_plan)
        assert len(cd.Concepts) > 5, "Did not map correctly."