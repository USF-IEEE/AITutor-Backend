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
        # cd = ConceptDatabase("TypeScript and Javascript Programming", "User wants to learn more about TypeScript, User wants to understand programming better, User wants to dive deeper in the theoretical aspects of Computer Science and also learn the power of Programming Languages.")
        # assert len(cd.Concepts) > 0, "Did not map correctly."
#         ds_alg_notes = """Tutor shall educate on the following concepts:
# - Main Concept: Data Structures and Algorithms
#   - Subconcept: Introduction to Data Structures and Memory
#   - Subconcept: Linear Data Structures
#     - Subconcept: Array
#     - Subconcept: Linked List
#       - Subconcept: Singly Linked List
#       - Subconcept: Doubly Linked List
#       - Subconcept: Circular Linked List
#     - Subconcept: Stack
#     - Subconcept: Queue
#   - Subconcept: Non-Linear Data Structures
#     - Subconcept: Trees
#       - Subconcept: Binary Tree
#       - Subconcept: Binary Search Tree
#       - Subconcept: AVL Tree
#       - Subconcept: Red-Black Tree
#       - Subconcept: B-Tree
#     - Subconcept: Heaps
#       - Subconcept: Max Heap
#       - Subconcept: Min Heap
#     - Subconcept: Graphs
#       - Subconcept: Directed Graph (Digraph)
#       - Subconcept: Undirected Graph
#       - Subconcept: Weighted Graph
#   - Subconcept: Time and Space Complexity Analysis
#     - Subconcept: Big O Notation
#     - Subconcept: Analysis of Algorithms
#       - Subconcept: Sorting Algorithms
#         - Subconcept: Bubble Sort
#         - Subconcept: Selection Sort
#         - Subconcept: Insertion Sort
#         - Subconcept: Merge Sort
#         - Subconcept: Quick Sort
#       - Subconcept: Searching Algorithms
#         - Subconcept: Linear Search
#         - Subconcept: Binary Search
#         - Subconcept: Hashing Algorithms
# The tutor will start with the introduction to data structures and memory, then proceed to cover linear data structures like arrays, linked lists, stacks, and queues. Next, the tutor will introduce non-linear data structures such as trees (including binary trees, binary search trees, AVL trees, Red-Black trees, and B-trees), heaps, and graphs (including directed, undirected, and weighted graphs). Finally, the tutor will cover time and space complexity analysis, including Big O notation and the analysis of various sorting and searching algorithms.
# This concept graph provides a structured learning path for the user to understand and learn about the desired topics in data structures and algorithms.
# """
#         cd = ConceptDatabase("Data Structures and Algorithms", ds_alg_notes)
#         assert len(cd.Concepts) > 5, "Did not map correctly."       
            sql_notes = """[0]: Main Concept: SQL
[1]: Student wants to learn about how SQL works.
[2]: Subconcept: Understanding Databases
[3]: Subconcept: SQL Syntax
[4]: Subconcept: DDL (Data Definition Language) Commands
[5]: Subconcept: DML (Data Manipulation Language) Commands
[6]: Subconcept: DCL (Data Control Language) Commands
[7]: Subconcept: SQL Joins
[8]: Subconcept: SQL Functions
[9]: Subconcept: SQL Views
[10]: Subconcept: SQL Constraints
[11]: Subconcept: SQL Indexes
[12]: Subconcept: SQL Sequences
[13]: "What aspects of SQL does the student specifically want to learn more about?"
[14]: "Does the student have any prior knowledge about SQL or databases?"
[15]: Student's current understanding level of SQL is 3/5.
[16]: "Student is interested in learning about Entity Relationship databases in SQL."
[17]: Subconcept: Entity Relationship Databases in SQL
[18]: "Does the student have any prior experience with Entity Relationship Databases?"
[19]: User is planning to create a web application with a state system.
[20]: "What experience does the student have in developing web applications?"
[21]: Subconcept: Web Applications and SQL
[22]: "Student is planning to work with SQLAlchemy and Django"      
[23]: "Student aims to build a complex database application"        
[24]: Subconcept: Using SQLAlchemy with Django
[25]: "Prior experience with Django or SQLAlchemy?"
[26]: "Preferable: a session focusing on integrating SQLAlchemy with Django"
[27]: "Does the student prefer a more hands-on, project-based approach to the learning process?"""
            cd = ConceptDatabase("SQL", sql_notes)    
            assert len(cd.Concepts) > 5, "Did not map correctly."