import ollama
print("hello1")
response = ollama.chat(
    model="mistral",
    messages=[
        {"role": "user", "content": "Explain AI in one sentence"}
    ]
)
print("hello")

print(response["message"]["content"])







