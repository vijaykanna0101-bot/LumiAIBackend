import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return jsonify({"app": "LUMI AI Backend", "status": "online"})

@app.post("/chat")
def chat():
    if not os.environ.get("GROQ_API_KEY"):
        return jsonify({"error": "AI service is not configured"}), 503

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400
    if len(message) > 12000:
        return jsonify({"error": "Message is too long"}), 413

    try:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        result = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are LUMI, a helpful AI assistant."},
                {"role": "user", "content": message}
            ],
            reasoning_effort="medium",
            max_completion_tokens=1500
        )
        return jsonify({
            "reply": result.choices[0].message.content or "I couldn't generate a reply."
        })
    except Exception:
        app.logger.exception("Groq request failed")
        return jsonify({"error": "AI request failed. Please try again."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
