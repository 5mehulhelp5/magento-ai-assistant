# 🧠 Magento AI Assistant

An intelligent multilingual assistant that connects with Magento to provide semantic product search, PDF-based enrichment, and conversational AI via FastAPI + LangChain.

---

## 🏗️ System Architecture

![Architecture](docs/architecture.png)

### Data Flow
1. **Magento API** — Fetches products and metadata.
2. **ETL / Data Ingestion** — Cleans and preprocesses Magento product data.
3. **PDF Processing** — Extracts specifications from manuals and links to SKUs.
4. **FAISS Index** — Embeds descriptions/specs for semantic search.
5. **FastAPI Backend** — Exposes `/search` and `/chat` endpoints for use by frontend or Magento store.
6. **Frontend / Chat UI** — Web-based or Magento-integrated chatbot.
7. **Redis / Cron** — Manages sync state and weekly updates.

---

## ⚙️ Core Technologies

| Layer | Tools / Frameworks |
|-------|--------------------|
| Backend API | FastAPI |
| AI / NLP | LangChain, Sentence-Transformers, XLM-RoBERTa |
| Embeddings Store | FAISS |
| Data Source | Magento REST API |
| Document Parsing | PyMuPDF |
| Deployment | Docker / AWS / Heroku |
| Optional | Redis (state/session), DeepL (translation) |

---

## 🚀 Setup Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/magento-ai-assistant.git
cd magento-ai-assistant
