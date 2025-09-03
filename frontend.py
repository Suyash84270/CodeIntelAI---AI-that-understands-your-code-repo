import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  # FastAPI backend

st.set_page_config(page_title="AI Repo Assistant", page_icon="🤖", layout="wide")
st.title(" AI Repo Assistant")
st.write("Upload a repo, ask questions, and get summaries!")

# ---------------- SESSION STATE ----------------
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []  # store (question, answer)

# ---------------- File Upload ----------------
st.header("📂 Upload Repository")
uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_file:
    with st.spinner("Uploading and indexing repo..."):
        response = requests.post(
            f"{API_URL}/upload_repo/",
            files={"file": uploaded_file}
        )
    if response.status_code == 200:
        st.success(f"✅ Repo indexed: {response.json()}")
    else:
        st.error(f"❌ Upload failed: {response.text}")

# ---------------- Ask Questions ----------------
st.header("❓ Ask a Question")
query = st.text_input("Enter your question about the repo:")

if st.button("Ask"):
    if query:
        with st.spinner("Thinking..."):
            response = requests.post(f"{API_URL}/ask/", data={"query": query})
        if response.status_code == 200:
            answer = response.json()["answer"]
            # Save to session history
            st.session_state.qa_history.append((query, answer))
            st.success(answer)
        else:
            st.error("⚠️ Failed to get answer.")

# ---------------- Show Q&A History ----------------
if st.session_state.qa_history:
    st.subheader("📜 Question & Answer History")
    for q, a in reversed(st.session_state.qa_history):
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")
        st.markdown("---")

# ---------------- Summarize File ----------------
st.header("📄 Summarize a File")
filename = st.text_input("Enter filename (e.g., auth.py):")

if st.button("Summarize"):
    if filename:
        with st.spinner("Summarizing file..."):
            response = requests.post(f"{API_URL}/summarize_file/", data={"filename": filename})
        if response.status_code == 200:
            st.write("**Summary:**")
            st.info(response.json()["summary"])
        else:
            st.error("⚠️ Failed to summarize.")
