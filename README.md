#  CodeIntelAI – AI that Understands Your Code Repo

**CodeIntelAI** is an **AI-powered assistant** that can read your code repository, answer natural language questions, and summarize files.  

It is built with a **FastAPI backend** for AI logic and a **Streamlit frontend** for an interactive UI – simulating a real-world **AI microservice architecture**.

---

##  Features
1) Upload any code repository (as `.zip`)  
2) Ask natural language questions about the repo  
3) Summarize individual Python files in plain English  
4) Retrieves function/class definitions with **line numbers**  
5) Uses **FAISS + embeddings** for semantic code search  
6) Backend powered by **FastAPI** + Hugging Face LLM  
7) Frontend powered by **Streamlit** for recruiters & non-tech users  

---

##  Architecture

```mermaid
graph TD;
    A[Streamlit Frontend] <--> B[FastAPI Backend];
    B --> C[LLM: LaMini-T5-738M];
    B --> D[Embeddings: all-MiniLM-L6-v2];
    D --> E[FAISS Vector Store];
    B --> F[Code Parser + Line Numbers];
