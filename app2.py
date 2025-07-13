
from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import fitz  # PyMuPDF
import traceback

app = Flask(__name__)
CORS(app)

# Global
doc_chunks = []
faiss_index = None
doc_text = ""
summary = ""
logic_question = ""
logic_answer = ""

# Load embedding + llama model (TinyLLaMA = fast + safe)
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
llm = Llama(
    model_path="models/7B/llama-2-7b.Q4_K_M.gguf",
    n_ctx=2048,
    use_mlock=False,
    verbose=True
)

def parse_document(file_stream, filename):
    global doc_text
    text = ""
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    else:
        text = file_stream.read().decode('utf-8', errors='ignore')
    doc_text = text
    return text

def create_chunks(text, max_chars=800):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for para in paragraphs:
        while len(para) > max_chars:
            chunks.append(para[:max_chars])
            para = para[max_chars:]
        chunks.append(para)
    return chunks

def build_index(chunks):
    global faiss_index
    embeddings = embed_model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss_index = index

def summarize_chunks(chunks):
    summary_parts = []
    for i, chunk in enumerate(chunks):
        short_chunk = chunk[:800]
        prompt = f"Summarize this:\n{short_chunk}"
        try:
            res = llm.create_completion(prompt, max_tokens=128, stop=["\n"])
            part = res['choices'][0]['text'].strip()
            summary_parts.append(f"- {part}")
        except Exception as e:
            print(f"[WARNING] Chunk {i+1} failed: {e}")
    return "\n".join(summary_parts)

@app.route('/upload', methods=['POST'])
def upload():
    global doc_chunks, summary, logic_question, logic_answer
    logic_question = ""
    logic_answer = ""
    summary = ""

    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        text = parse_document(file.stream, file.filename)
        doc_chunks = create_chunks(text)
        build_index(doc_chunks)

        summary = summarize_chunks(doc_chunks[:5])  # summarize top 5 chunks
        return jsonify({"summary": summary})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question or not faiss_index:
        return jsonify({"error": "Invalid request"}), 400

    q_emb = embed_model.encode([question])
    distances, indices = faiss_index.search(np.array(q_emb), k=3)
    top_chunks = [doc_chunks[i] for i in indices[0] if i < len(doc_chunks)]
    context = "\n---\n".join(top_chunks)[:1500]

    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        f"Answer using only the context and cite the part used."
    )
    # res = llm.create_completion(prompt, max_tokens=150, stop=["\n"])
    # answer = res['choices'][0]['text'].strip()
    # citation = top_chunks[0][:80].replace("\n", " ") + "..."
    # return jsonify({"answer": f"{answer} (Source: \"{citation}\")"})
    try:
        res = llm.create_completion(prompt, max_tokens=128, stop=["\n"])
        response = res['choices'][0]['text'].strip()
        citation = top_chunks[0][:80].replace("\n", " ") + "..."
        return jsonify({"answer": f"{answer} (Source: \"{citation}\")"})
    except Exception as e:
        print("[LLM ERROR]", e)
        response = "[LLM error: unable to generate response]"

@app.route('/generate_question', methods=['GET'])
def generate_question():
    global logic_question, logic_answer
    if not doc_text:
        return jsonify({"error": "No document loaded"}), 400

    try:
        context = doc_text[:1000]  # Limit input text
        prompt = (
            f"From the following text, create ONE logic-based question and its answer:\n\n{context}\n\n"
            f"Format:\nQuestion: ...\nAnswer: ..."
        )

        res = llm.create_completion(prompt, max_tokens=150, stop=["Question:", "Answer:"])
        text = res['choices'][0]['text'].strip()

        if "Question:" in text and "Answer:" in text:
            parts = text.split("Answer:")
            logic_question = parts[0].replace("Question:", "").strip()
            logic_answer = parts[1].strip()
        else:
            logic_question = "[Could not extract logic question]"
            logic_answer = "[Unknown]"

        return jsonify({"question": logic_question})

    except Exception as e:
        print("[ERROR in /generate_question]", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to generate question"}), 500

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    user_answer = data.get("answer", "").strip().lower()
    if not logic_answer:
        return jsonify({"error": "No logic question generated"}), 400

    correct = user_answer == logic_answer.lower().strip()
    return jsonify({
        "correct": correct,
        "correct_answer": logic_answer
    })

if __name__ == '__main__':
    app.run(port=5000)
