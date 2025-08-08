import sys, os, json, requests

HISTORY_FILE = "chat_history.json"
API_URL = "http://localhost:11434/api/chat" # Default Ollama API URL
MODEL = "qwen3:14b"
STREAM_ARG = "--stream-disabled"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def export_to_markdown(history, filename="chat_history.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 🧠 Ollama Chat History\n\n")
        for i, msg in enumerate(history):
            role = "👤 You" if msg["role"] == "user" else "🤖 AI"
            f.write(f"### {role} (Turn {i+1})\n")
            f.write(f"{msg['content']}\n\n")
    print(f"\n✅ Exported to {filename}")


def chat(prompt):
    history = load_history()
    history.append({"role": "user", "content": prompt})
    print("\n AI is thinking...")
    reply = send_chat_request(prompt, history, stream=False)
    print("\n🤖 AI:", reply)

    history.append({"role": "assistant", "content": reply})
    save_history(history)
    export_to_markdown(history)

def chat_stream(prompt):
    history = load_history()
    history.append({"role": "user", "content": prompt})

    reply = send_chat_request(prompt, history, stream=True)

    history.append({"role": "assistant", "content": reply})
    save_history(history)
    export_to_markdown(history)

def send_chat_request(prompt, history, stream=False):
    response = requests.post(API_URL, json={
        "model": MODEL,
        "messages": history,
        "stream": stream
    }, stream=stream)

    reply = ""

    if stream:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                if "message" in chunk and "content" in chunk["message"]:
                    text = chunk["message"]["content"]
                    print(text, end="", flush=True)
                    reply += text
                if chunk.get("done", False):
                    break
    else:
        reply = response.json()["message"]["content"]
    return reply


def chat_with_user_input(stream_mode=False):
    while True:
        user_input = input("\n🧑 You ")

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        if stream_mode:
            chat_stream(user_input)
        else:
            chat(user_input)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == STREAM_ARG:
        print("💬 Start chatting with Qwen3. Type 'exit' to quit.")
        chat_with_user_input()
    else:
        print("💬 Stream mode enabled. Start chatting with Qwen3. Type 'exit' to quit.")
        chat_with_user_input(stream_mode=True)



