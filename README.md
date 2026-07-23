# 📄 PDF Chatbot RAG


> A production-ready Retrieval-Augmented Generation (RAG) chatbot that enables users to upload PDF documents and ask natural language questions powered by Google Gemini, LangChain, and FAISS.



<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/FAISS-0467DF?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Clean%20Architecture-4CAF50?style=for-the-badge"/>
</p>

---

## 🔗 Live Demo & Repository

- 🚀 **Live Demo:** [genish222-pdf-chat.streamlit.app](https://genish222-pdf-chat.streamlit.app/)
- 💻 **Repository:** [github.com/Genish222/pdf-chatbot-rag](https://github.com/Genish222/pdf-chatbot-rag)

> ⚠️ **Note:** The live demo runs on Streamlit Community Cloud's free tier — the
> app may take 30–60 seconds to wake up if it's been idle, and uploaded PDFs
> are cleared whenever the app restarts.


---

## ✨ Features

- 📄 Upload one or more PDF documents
- 🤖 Ask questions in natural language
- 🔍 Semantic search using FAISS vector database
- 🧠 Google Gemini-powered contextual responses
- 📚 Retrieval-Augmented Generation (RAG)
- ⚡ Fast document chunking and indexing
- 🏗️ Clean Architecture implementation
- 🎨 Interactive Streamlit interface
- 🔒 Environment-based configuration
- 📦 Modular and production-ready codebase

---

# 🏛️ Architecture

This project follows **Clean Architecture**, separating business logic from external frameworks.

```
                 ┌──────────────────────┐
                 │     Presentation     │
                 │      Streamlit UI    │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │     Application      │
                 │ Document & Chat Flow │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │        Domain        │
                 │ Models • Ports • DTO │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │    Infrastructure    │
                 │ Gemini • FAISS • PDF │
                 └──────────────────────┘
```

---

# 📂 Project Structure

```
pdf-chatbot-rag/
│
├── app/
│   └── main.py
│
├── src/
│   ├── application/
│   ├── config/
│   ├── domain/
│   ├── infrastructure/
│   └── presentation/
│
├── data/
│   ├── uploads/
│   └── vectorstores/
│
├── tests/
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# ⚙️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| UI | Streamlit |
| LLM | Google Gemini |
| Framework | LangChain |
| Vector Database | FAISS |
| PDF Parsing | PyPDF |
| Architecture | Clean Architecture |

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/pdf-chatbot-rag.git
cd pdf-chatbot-rag
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file.

```
GOOGLE_API_KEY=YOUR_API_KEY
```

---

## 5. Run the application

```bash
streamlit run app/main.py
```

---

# 🧠 How It Works

```
PDF Upload
      │
      ▼
Extract Text
      │
      ▼
Split into Chunks
      │
      ▼
Gemini Embeddings
      │
      ▼
FAISS Vector Store
      │
      ▼
User Question
      │
      ▼
Similarity Search
      │
      ▼
Relevant Context
      │
      ▼
Gemini LLM
      │
      ▼
Final Answer
```

---

# 📸 Screenshots

### Home
> <img width="1888" height="904" alt="image" src="https://github.com/user-attachments/assets/9664dd6b-7a22-4962-a26b-994e97812b08" />

### Uploading & Indexing a PDF
<img width="313" height="846" alt="image" src="https://github.com/user-attachments/assets/392b14f0-efde-467d-808c-29ce0bfd88ca" />


### Chatting with your Document
<img width="1902" height="911" alt="image" src="https://github.com/user-attachments/assets/2013b1bb-758a-4058-a006-f0d15868236f" />
<img width="1879" height="908" alt="image" src="https://github.com/user-attachments/assets/99ee2f7f-324c-41d1-aaec-2a2faeb294ad" />




---

# 📈 Current Status

### ✅ Completed

- PDF Upload
- PDF Parsing
- Text Chunking
- Gemini Embeddings
- FAISS Vector Store
- Retrieval Pipeline
- Gemini Chat
- Streamlit UI
- Clean Architecture
- Environment Configuration

---

# 🔮 Future Improvements

- Multi-PDF Support
- Chat History
- Source Citation
- Conversation Memory
- Docker Support
- Authentication
- Cloud Deployment
- Unit & Integration Tests

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to GitHub

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a Star!

Built with ❤️ using **Python**, **LangChain**, **Google Gemini**, **FAISS**, and **Streamlit**

</div>
