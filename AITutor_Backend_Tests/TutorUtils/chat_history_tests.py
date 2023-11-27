import unittest
from AITutor_Backend.src.TutorUtils.chat_history import *

class ChatHistoryTests(unittest.TestCase):
    def test_chat_history_initialization(self):
        chat_history = ChatHistory()
        self.assertEqual(len(chat_history.chat), 1, "Chat history should initially contain one entry.")

    def test_adding_user_response(self):
        chat_history = ChatHistory()
        user_prompt = "This is a test user prompt."
        chat_history.hear(user_prompt)
        self.assertEqual(len(chat_history.chat), 2, "Chat history should contain two entries after adding user response.")

    def test_adding_tutor_response(self):
        chat_history = ChatHistory()
        tutor_response = "This is a test tutor response."
        chat_history.respond(tutor_response)
        self.assertEqual(len(chat_history.chat), 2, "Chat history should contain two entries after adding tutor response.")

    def test_env_string_output(self):
        chat_history = ChatHistory()
        self.assertIsInstance(chat_history.env_string(), str, "env_string should return a string.")

    def test_serialization_to_sql(self):
        chat_history = ChatHistory()
        self.assertIsInstance(chat_history.to_sql(), str, "to_sql should return a string.")

    def test_deserialization_from_sql(self):
        original_chat_history = ChatHistory()
        serialized_data = original_chat_history.to_sql()
        new_chat_history = ChatHistory.from_sql(serialized_data)
        self.assertEqual(original_chat_history.chat, new_chat_history.chat, "Deserialized chat history should match original.")

    def test_json_format(self):
        chat_history = ChatHistory()
        self.assertIsInstance(chat_history.format_json(), dict, "format_json should return a dictionary.")
