#  AI Repo Assistant

An interactive tool to **upload repositories, ask code-related questions, and get summaries** using FastAPI + Streamlit + LLMs.

##  Features
- Upload a `.zip` repository
- Ask natural language questions about the code
- Get file-level summaries in plain English
- Persistent Q&A history in the UI

##  Tech Stack
- **FastAPI** → Backend API
- **Streamlit** → Interactive frontend
- **Sentence Transformers + FAISS** → Embeddings & semantic search
- **LaMini-T5** → Lightweight summarization/Q&A LLM

##  Setup
```bash
git clone https://github.com/your-username/ai-repo-assistant.git
cd ai-repo-assistant
pip install -r requirements.txt
