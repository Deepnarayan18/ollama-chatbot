from flask import Flask, request
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma:2b"

user_sessions = {}

@socketio.on('connect', namespace='/chat')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")
    user_sessions[request.sid] = []

@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}")
    user_sessions.pop(request.sid, None)

@socketio.on('user_message', namespace='/chat')
def handle_user_message(data):
    message = data.get("message")
    if not message:
        return

    print(f"📨 User ({request.sid}): {message}")

    chat_history = user_sessions.get(request.sid, [])

    payload = {
        "model": OLLAMA_MODEL,
        "messages": chat_history + [{"role": "user", "content": message}],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        reply = response.json()["message"]["content"]
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": reply})
        user_sessions[request.sid] = chat_history
        emit("bot_reply", {"reply": reply}, namespace='/chat')
    except Exception as e:
        print("❌ Ollama error:", e)
        emit("bot_reply", {"reply": "⚠️ Backend error."}, namespace='/chat')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
