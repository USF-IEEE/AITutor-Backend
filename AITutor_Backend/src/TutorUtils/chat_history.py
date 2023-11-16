class ChatHistory:
        def __init__(self,):
            self.chat = ["AI Tutor:\nHey I am your AI Tutor. How can I help you today?",]
        def hear(self, user_prompt,):
            self.chat += [f"\Student:\n{user_prompt}"]
        def respond(self, tutor_response):
            self.chat += [f"\nAI Tutor:{tutor_response}"]
        def env_string(self,):
            """returns environment formatted string.

            Returns:
                str: environment formatted string of chat history
            """
            return "\n".join(self.chat)