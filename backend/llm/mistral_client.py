import ollama
import subprocess
import requests
import time


def ensure_ollama_running():
    try:
        requests.get("http://localhost:11434", timeout=2)
    except:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)


def call_llm(prompt: str) -> str:
    ensure_ollama_running()

    response = ollama.chat(
        model="mistral",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cybersecurity policy analysis assistant. "
                    "Follow the instructions strictly and return structured output."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.0,
            "num_predict": 900
        }
    )

    result = response["message"]["content"]

    # Debug output
    print("\n===== LLM OUTPUT =====")
    print(result)
    print("======================\n")

    return result.strip()