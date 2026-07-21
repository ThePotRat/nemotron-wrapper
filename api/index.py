import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

# Tell Flask where to look for the static frontend files
app = Flask(__name__, static_folder="../public", static_url_path="")

# Read NVIDIA API Key from environment variables
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)

# Load hidden system prompt
def _load_system_prompt():
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "system_prompt.txt"),
        os.path.join(os.path.dirname(__file__), "system_prompt.txt"),
        "system_prompt.txt",
    ]
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    return text
        except (FileNotFoundError, OSError):
            continue
    return "You are a helpful AI assistant."

SYSTEM_PROMPT = _load_system_prompt()

# Serve index.html at root "/"
@app.route("/", methods=["GET"])
def home():
    return send_from_directory("../public", "index.html")

# Chat endpoint
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_message = (data or {}).get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Empty message."}), 400

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        history = (data or {}).get("history", [])
        for turn in history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_message})

        completion = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b",
            messages=messages,
            temperature=1,
            top_p=0.95,
            max_tokens=4096,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 16384,
            },
        )
        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "AI service error."}), 500

# Health check
@app.route("/api/chat", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
