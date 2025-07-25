import os
import ollama
import json

class WhatsAppAI:
    def __init__(self, model_name, messages_file):
        """
        Initialize the WhatsAppAI with a local Ollama model and message file.
        """
        self.model_name = model_name
        self.messages = self.load_messages(messages_file)

    def load_messages(self, file_path):
        """
        Load and process WhatsApp chat messages from a .txt file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def format_messages(self):
        """
        Format messages into a structured conversation.
        """
        chat_history = []
        for line in self.messages:
            if '-' in line and ':' in line:
                try:
                    timestamp, message = line.split('-', 1)
                    sender, content = message.split(':', 1)
                    chat_history.append({"timestamp": timestamp.strip(), "sender": sender.strip(), "message": content.strip()})
                except ValueError:
                    continue  # Skip malformed lines
        return chat_history

    def ask_ai(self, query):
        """
        Ask a question about the entire chat history using the local Ollama model.
        """
        formatted_chat = self.format_messages()
        chat_context = json.dumps(formatted_chat)  # Use the entire chat history
        prompt = f"""
        Given the following complete WhatsApp chat history:
        {chat_context}
        Answer the question concisely:
        {query}
        """
        response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()

if __name__ == "__main__":
    model_name = "tinyllama"  # Fastest model for a MacBook Pro 2018
    messages_file = "messages.txt"  # Update with actual chat file path

    ai = WhatsAppAI(model_name, messages_file)

    while True:
        query = input("Ask a question about your chat (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        response = ai.ask_ai(query)
        print("AI Response:", response)
