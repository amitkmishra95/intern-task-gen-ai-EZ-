# intern-task-gen-ai-EZ-
# 🧠 GenAI Assistant

An intelligent document assistant that accepts uploaded PDF or TXT files, generates concise summaries, answers user queries based on document context, and challenges the user with logic-based questions using LLaMA and FAISS.

---

## 📌 Features

- 📄 Upload `.pdf` or `.txt` files
- ✍️ Extract and summarize key content using local LLaMA model
- ❓ Ask context-based questions
- 🧠 Logic-based challenge questions and evaluation

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/genai-assistant.git
cd genai-assistant

2. Set Up Backend (Flask)
bash
Copy
Edit
cd backend
python -m venv venv
venv\Scripts\activate      # On Windows
# or
source venv/bin/activate   # On Linux/Mac

pip install -r requirements.txt
3. Download Model
Download a compatible GGUF model (such as TinyLLaMA or Mistral-7B):

TinyLLaMA GGUF

Place the .gguf model in:

bash
Copy
Edit
backend/models/7B/llama-2-7b.Q4_K_M.gguf
Make sure the model name in the app.py matches the downloaded file.

4. Run Backend Server
bash
Copy
Edit
python app.py
This will start the Flask server at:

cpp
Copy
Edit
http://127.0.0.1:5000
5. Frontend (Optional Setup)
If using separate frontend:

Static HTML/JS:

bash
Copy
Edit
cd frontend
python -m http.server 8000
Visit: http://localhost:8000

Streamlit frontend:

bash
Copy
Edit
streamlit run app.py
🧠 Architecture & Flow
mathematica
Copy
Edit
1. Upload Document → Extract Text (PyMuPDF / TXT)
2. Create Chunks → Generate Embeddings (MiniLM)
3. Index with FAISS → Enable Similarity Search
4. Summarize Top Chunks → LLaMA Completion
5. Ask / Challenge → Use Context + LLaMA
6. Evaluate User Answer → Word Overlap
📦 APIs
Route	Method	Description
/upload	POST	Upload a file & get summary
/ask	POST	Ask a question about the file
/generate_question	GET	Generate one logic-based question
/evaluate	POST	Evaluate the user's answer

🛠 Technologies Used
Python, Flask

llama-cpp-python (for local LLaMA inference)

Sentence Transformers for embeddings

FAISS for similarity search

PyMuPDF (fitz) for PDF text extraction

Streamlit or HTML/JS for frontend (optional)

📂 Project Structure
bash
Copy
Edit
genai-assistant/
│
├── backend/
│   ├── app.py                 # Flask backend
│   ├── models/7B/             # LLaMA GGUF model
│   └── requirements.txt       # Backend dependencies
│
├── frontend/                  # Optional: frontend interface
│   └── index.html / app.py
│
└── README.md                  # This file
