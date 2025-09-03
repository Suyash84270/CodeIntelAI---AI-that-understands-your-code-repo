import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000"  # Change to your deployed FastAPI URL later

st.set_page_config(
    page_title="CodeIntelAI",
    page_icon="🤖",
    layout="wide"
)

st.title("CodeIntelAI — AI that understands your code repo")
st.write("Upload a repo, ask questions, and get instant answers or summaries.")

# ---------------- FILE UPLOAD ----------------
st.header("📂 Upload a Repository")
uploaded_file = st.file_uploader("Upload a zip file of your repo", type=["zip"])

if uploaded_file:
    with st.spinner("Uploading and indexing repo..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/upload_repo/", files={"file": uploaded_file})
        if response.status_code == 200:
            st.success(f"Repo uploaded ✅ - {response.json()}")
        else:
            st.error(f"Upload failed ❌: {response.text}")

# ---------------- ASK QUESTIONS ----------------
st.header("💬 Ask Questions About the Repo")
query = st.text_input("Enter your question (e.g., 'Where is the login function defined?')")

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(f"{API_URL}/ask/", data={"query": query})
            if response.status_code == 200:
                st.info(response.json()["answer"])
            else:
                st.error("Error: " + response.text)

# ---------------- SUMMARIZE FILE ----------------
st.header("📝 Summarize a File")
filename = st.text_input("Enter filename (e.g., auth.py)")

if st.button("Summarize"):
    if not filename.strip():
        st.warning("Please enter a filename.")
    else:
        with st.spinner("Summarizing..."):
            response = requests.post(f"{API_URL}/summarize_file/", data={"filename": filename})
            if response.status_code == 200:
                st.success(response.json()["summary"])
            else:
                st.error("Error: " + response.text)
