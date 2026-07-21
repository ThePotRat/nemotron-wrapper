import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# The NVIDIA API key is read from Vercel Environment Variables.
# NEVER hard-code it here.
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)

# ------------------------------------------------------------------
# HIDDEN SYSTEM PROMPT (loaded from system_prompt.txt, server-side only)
# ------------------------------------------------------------------
def _load_system_prompt():
    # Look in the repo root (one level up from api) and next to this file.
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
    # Fallback so the app still works if the file is missing.
    return "You are a helpful AI assistant."

SYSTEM_PROMPT = _load_system_prompt()

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_message = (data or {}).get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Empty message."}), 400

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Optional: accept prior conversation history from the client
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
        # Never leak internal details to the browser
        print("Error:", e)
        return jsonify({"error": "AI service error."}), 500

# Health check for the serverless function
@app.route("/api/chat", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
