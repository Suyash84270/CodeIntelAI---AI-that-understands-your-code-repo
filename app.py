import os
import zipfile
import pickle
import faiss
from fastapi import FastAPI, UploadFile, Form
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

# ---------------- CONFIG ----------------
UPLOAD_DIR = "uploads"
INDEX_PATH = "faiss.index"
DOCS_PATH = "docs.pkl"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- LLM LOADING ----------------
print("⚡ Loading LLM: MBZUAI/LaMini-T5-738M (optimized for QA & summarization)")
try:
    model_name = "MBZUAI/LaMini-T5-738M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
except Exception as e:
    print(f"❌ LLM failed to load: {e}")
    generator = None  # fallback

# ---------------- VECTOR STORE ----------------
class VectorStore:
    def __init__(self):
        self.index = None
        self.docs = []
        self.metas = []
        # ✅ Always initialize embedder
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add(self, text, meta):
        vec = self.embedder.encode([text])
        if self.index is None:
            self.index = faiss.IndexFlatL2(vec.shape[1])
        self.index.add(vec)
        self.docs.append(text)
        self.metas.append(meta)

    def search(self, query, top_k=3):
        if not self.index or not self.docs:
            return []
        vec = self.embedder.encode([query])
        D, I = self.index.search(vec, top_k)
        return [(self.metas[i], self.docs[i]) for i in I[0] if i < len(self.docs)]

    def save(self):
        if self.index:
            faiss.write_index(self.index, INDEX_PATH)
            with open(DOCS_PATH, "wb") as f:
                pickle.dump((self.docs, self.metas), f)

    def load(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(DOCS_PATH, "rb") as f:
                self.docs, self.metas = pickle.load(f)
        # ✅ Ensure embedder exists even after load
        if not hasattr(self, "embedder"):
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

vs = VectorStore()

# ---------------- HELPERS ----------------
def enforce_plain_english(text: str) -> str:
    """Ensure model output is plain English and not raw code."""
    lines = text.split("\n")
    cleaned = []
    for l in lines:
        if l.strip().startswith("def ") or l.strip().startswith("class "):
            continue
        cleaned.append(l.strip())
    return " ".join(cleaned).strip() or "⚠️ Could not generate a clear answer."

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="AI Repo Assistant", description="Ask questions & summarize repos", version="1.0")

@app.post("/upload_repo/")
async def upload_repo(file: UploadFile):
    """Upload and index a repo zip file."""
    try:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())

        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(UPLOAD_DIR)

        # Reset vector store
        vs.index = None
        vs.docs, vs.metas = [], []
        vs.embedder = SentenceTransformer("all-MiniLM-L6-v2")  # ✅ ensure reset

        # Index .py files
        for root, _, files in os.walk(UPLOAD_DIR):
            for fname in files:
                if fname.endswith(".py"):
                    with open(os.path.join(root, fname), "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    vs.add(code, fname)

        vs.save()
        return {"status": "Repo indexed", "chunks": len(vs.docs)}
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

@app.post("/ask/")
async def ask(query: str = Form(...)):
    """Ask a natural language question about repo."""
    try:
        vs.load()
        results = vs.search(query)

        if not results:
            return {"query": query, "answer": "No indexed code available. Please upload a repo first."}

        context = "\n".join([f"{meta}: {doc}" for meta, doc in results])

        prompt = f"""
You are an assistant that answers code-related questions.

Question: {query}
Relevant code snippets:
{context}

Answer in plain English (max 3 sentences, no raw code).
"""

        if generator is None:
            return {"query": query, "answer": "⚠️ LLM not loaded properly."}

        raw = generator(prompt, max_length=200)[0]["generated_text"]
        answer = enforce_plain_english(raw)

        return {"query": query, "answer": answer}
    except Exception as e:
        return {"query": query, "answer": f"⚠️ Error in /ask: {str(e)}"}

@app.post("/summarize_file/")
async def summarize_file(filename: str = Form(...)):
    """Summarize a file in the uploaded repo."""
    try:
        vs.load()
        relevant = [(meta, doc) for meta, doc in zip(vs.metas, vs.docs) if filename in meta]

        if not relevant:
            return {"error": f"No file named {filename} found in indexed repo."}

        code_text = "\n".join([doc for _, doc in relevant])[:2500]

        prompt = f"""
You are an assistant that summarizes Python files.

File: {filename}
Code:
{code_text}

Write a short English summary. Describe what functions and classes do (max 5 sentences).
"""

        if generator is None:
            return {"filename": filename, "summary": "⚠️ LLM not loaded properly."}

        raw = generator(prompt, max_length=250)[0]["generated_text"]
        summary = enforce_plain_english(raw)

        return {"filename": filename, "summary": summary}
    except Exception as e:
        return {"filename": filename, "summary": f"⚠️ Error in /summarize_file: {str(e)}"}
