import ollama
import logging

# Ollama configuration
model = 'gemma2:2b'
messages = []

# Roles for chat history
USER = 'user'
ASSISTANT = 'assistant'

def add_history(content, role):
    messages.append({'role': role, 'content': content})

def chat(message):
    add_history(message, USER)
    response = ollama.chat(model=model, messages=messages, stream=True)
    complete_message = ''
    for line in response:
        complete_message += line['message']['content']
    add_history(complete_message, ASSISTANT)
    return complete_message