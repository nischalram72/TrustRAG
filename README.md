# TrustRAG: Verification Engine


**Don't just answer. Prove it.**

An agentic Retrieval-Augmented Generation (RAG) system that fact-checks its own answers against source documents before showing them to the user. Built specifically for high-stakes domains (like financial analysis) where a hallucination is significantly worse than a refusal to answer.

---

## 🛑 The Problem

Standard RAG pipelines suffer from a critical flaw: when they fail to retrieve the correct context, the LLM will often "helpfully" hallucinate an answer based on its pre-trained knowledge, rather than admitting it doesn't know. In domains like finance, law, or healthcare, a confident hallucination can lead to catastrophic decisions. 

We needed a system that guarantees **groundedness**—if the answer isn't explicitly in the provided documents, the system must refuse to answer.

## 💡 What Makes TrustRAG Different?

Unlike standard RAG (Retrieve $\rightarrow$ Generate), TrustRAG implements an **Agentic Verification Loop**:

1. **Drafting**: The agent retrieves context and drafts an answer.
2. **The Independent Judge**: Before the user ever sees the answer, a secondary LLM strictly evaluates the draft against the retrieved chunks. 
3. **Self-Correction**: If the judge detects unsupported claims, the agent *catches the hallucination*, reformulates the search query using different keywords, and tries again.
4. **Hard Refusal**: If the agent exhausts its retries without achieving a high confidence score from the judge, it explicitly refuses to answer and provides an audit trail explaining why.

## 🏗️ Architecture

- **Data Ingestion**: Parses PDFs (`PyPDF2`), chunks text, and generates vector embeddings via Google Gemini.
- **Vector Store**: Local `ChromaDB` for fast semantic similarity search.
- **LLM Engine**: Google Gemini 2.5 Flash handles both the Drafting and the strict Verification Judge roles.
- **Orchestration**: Custom Python agent loop with `tenacity` for exponential backoff and API rate-limit resilience.
- **User Interface**: A highly customized `Streamlit` frontend featuring a cinematic, dark "Ledger" aesthetic, pure CSS animations, and a transparent Audit Trail expander.

## 📊 Evaluation Results

We ran a benchmark of adversarial and out-of-context questions against the system to test the strictness of the Verification Judge.

| Metric | Result |
|--------|--------|
| Total Questions Tested | 192 |
| Confirmed Hallucinations | **6** |
| Precision (Groundedness) | 96.9% |

*The system successfully identified missing context and triggered safe "refusals" instead of hallucinating data.*

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- A Google Gemini API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nischalram72/TrustRAG.git
   cd TrustRAG
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

4. **Run the Application:**
   ```bash
   streamlit run app/streamlit_app.py
   ```
   The UI will be available at `http://localhost:8501`.

## 🔮 What I'd Improve Next

While the core verification loop is highly effective, here is what I would tackle next to make the system enterprise-ready:

1. **Advanced Document Parsing (OCR)**: Currently relying on standard text extraction. Integrating OCR (like Tesseract) or a multimodal approach would allow the system to accurately parse complex financial tables and charts from 10-K reports.
2. **Hybrid Search**: Upgrading from pure dense vector search to a Hybrid Search (combining BM25 keyword search with Vector search) to improve retrieval recall for specific acronyms or serial numbers.
3. **Streaming Responses**: The Verification Loop adds latency. Implementing token streaming for the final verified answer would drastically improve perceived performance for the end user.
4. **React/Next.js Frontend**: While the custom CSS makes Streamlit look beautiful, migrating to a dedicated Next.js frontend would allow for vastly more complex animations and state management.
