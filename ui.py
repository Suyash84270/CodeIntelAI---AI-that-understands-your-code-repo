import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"  # Backend FastAPI URL

st.set_page_config(page_title="AI Dev Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Knowledge Assistant for Developers")
st.write("Upload your repo and ask questions about the codebase.")

# ---- Upload Section ----
st.subheader("📂 Upload Repository")
uploaded_file = st.file_uploader("Upload a .zip file of your repo", type=["zip"])

if uploaded_file is not None:
    with st.spinner("Uploading and indexing repo..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/zip")}
        res = requests.post(f"{FASTAPI_URL}/upload_repo/", files=files)
        if res.status_code == 200:
            st.success(f"✅ Repo indexed with {res.json()['chunks']} chunks")
        else:
            st.error("❌ Upload failed")

# ---- Ask Section ----
st.subheader("💬 Ask Questions About Your Codebase")
query = st.text_input("Enter your question:")

if st.button("Ask") and query:
    with st.spinner("Thinking..."):
        data = {"query": query}
        res = requests.post(f"{FASTAPI_URL}/ask/", data=data)
        if res.status_code == 200:
            answer = res.json()["answer"]
            st.write("### 🔎 Results:")
            if isinstance(answer, list):
                for a in answer:
                    st.markdown(f"**📍 {a['location']}**")
                    st.info(a['explanation'])
            else:
                st.info(answer)
        else:
            st.error("❌ Query failed")
