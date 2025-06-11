import pickle
import os
import streamlit as st
import uuid
import socketio

st.set_page_config(page_title="🧠 Real-time LLM Chat (File Persistence)", layout="centered")

# Generate or retrieve a unique user ID (for file naming)
user_id = str(uuid.uuid4())
filename = f"messages_{user_id}.pkl"

def load_messages():
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return []

def save_messages(messages):
    with open(filename, "wb") as f:
        pickle.dump(messages, f)

messages = load_messages()

# Socket.IO client (for sending only)
sio = socketio.Client()

try:
    if not sio.connected:
        sio.connect("http://localhost:5000", namespaces=['/chat'])
except Exception as e:
    st.error(f"❌ Could not connect to backend: {e}")

st.title("💬 Chat with Local LLM (File Persistence)")

# Display messages
for sender, msg in messages:
    st.chat_message("user" if sender == "user" else "assistant").write(msg)

# Poll for new messages
if st.button("Check for new messages"):
    new_messages = load_messages()
    if len(new_messages) > len(messages):
        messages = new_messages
        st.rerun()

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    messages.append(("user", user_input))
    save_messages(messages)
    sio.emit("user_message", {
        "user_id": user_id,
        "message": user_input
    }, namespace='/chat')
    # Optionally, you can add a small delay and poll here, but it's not perfect
    # For demo purposes, just rerun to show the user message
    st.rerun()
