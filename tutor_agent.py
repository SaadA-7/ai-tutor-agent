import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

print("Welcome to your AI Tutor!")

# Keep conversation history
history = [
    {"role": "user", "content": "You are an AI tutor. Answer questions clearly and helpfully. Be friendly, and explain things step-by-step if helpful."},
]

while True:
    user_input = input("Ask a question (or type 'exit'): ")
    if user_input.lower() == "exit":
        break

    # Append user's input to history
    history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.5,
        messages=history,
    )

    answer = response.content[0].text.strip()
    print("Tutor:", answer)

    # Append assistant's reply to history
    history.append({"role": "assistant", "content": answer})
