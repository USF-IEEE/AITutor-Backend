import unittest
from AITutor_Backend.src.TutorUtils.concepts import *

class NotebankTests(unittest.TestCase):
    def test_concept_graph(self,):
        cd = ConceptDatabase("", debug=True)
        c1 = Concept("Concept 1", "")
        cd.Concepts.append(c1)
        c2 = Concept.create_from_concept_string_add_to_database("Concept 2", "Concept string mapping it to <Concept>Concept 1</Concept> which is super important.", "", cd)

        assert c1 in c2.refs, "Did not map correctly."
        assert c1 in c2.definition, "Did not map correctly"
    
    def test_generate_concept_graph(self,):
        # cd = ConceptDatabase("TypeScript and Javascript Programming", "User wants to learn more about TypeScript, User wants to understand programming better, User wants to dive deeper in the theoretical aspects of Computer Science and also learn the power of Programming Languages.")
        # assert len(cd.Concepts) > 0, "Did not map correctly."
        ds_alg_notes = """Tutor shall educate on the following concepts:
- Main Concept: Data Structures and Algorithms
  - Subconcept: Introduction to Data Structures and Memory
  - Subconcept: Linear Data Structures
    - Subconcept: Array
    - Subconcept: Linked List
      - Subconcept: Singly Linked List
      - Subconcept: Doubly Linked List
      - Subconcept: Circular Linked List
    - Subconcept: Stack
    - Subconcept: Queue
  - Subconcept: Non-Linear Data Structures
    - Subconcept: Trees
      - Subconcept: Binary Tree
      - Subconcept: Binary Search Tree
      - Subconcept: AVL Tree
      - Subconcept: Red-Black Tree
      - Subconcept: B-Tree
    - Subconcept: Heaps
      - Subconcept: Max Heap
      - Subconcept: Min Heap
    - Subconcept: Graphs
      - Subconcept: Directed Graph (Digraph)
      - Subconcept: Undirected Graph
      - Subconcept: Weighted Graph
  - Subconcept: Time and Space Complexity Analysis
    - Subconcept: Big O Notation
    - Subconcept: Analysis of Algorithms
      - Subconcept: Sorting Algorithms
        - Subconcept: Bubble Sort
        - Subconcept: Selection Sort
        - Subconcept: Insertion Sort
        - Subconcept: Merge Sort
        - Subconcept: Quick Sort
      - Subconcept: Searching Algorithms
        - Subconcept: Linear Search
        - Subconcept: Binary Search
        - Subconcept: Hashing Algorithms
The tutor will start with the introduction to data structures and memory, then proceed to cover linear data structures like arrays, linked lists, stacks, and queues. Next, the tutor will introduce non-linear data structures such as trees (including binary trees, binary search trees, AVL trees, Red-Black trees, and B-trees), heaps, and graphs (including directed, undirected, and weighted graphs). Finally, the tutor will cover time and space complexity analysis, including Big O notation and the analysis of various sorting and searching algorithms.
This concept graph provides a structured learning path for the user to understand and learn about the desired topics in data structures and algorithms.
"""
        cd = ConceptDatabase("Data Structures and Algorithms", ds_alg_notes)
        assert len(cd.Concepts) > 5, "Did not map correctly."
