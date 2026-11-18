import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=15, max=60))
def generate_answer(question: str, chunks: list) -> str:
    """
    Calls the Gemini API to answer the question based on the provided chunks.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")
        
    # Prepare the context by joining the chunks' text
    # We include the source and chunk_id so the LLM knows what to cite!
    context_parts = []
    for c in chunks:
        source = c.get("source", "Unknown Source")
        chunk_id = c.get("chunk_id", "Unknown ID")
        text = c.get("text", "")
        context_parts.append(f"[Source: {source}, Chunk ID: {chunk_id}]\n{text}")
        
    context = "\n\n".join(context_parts)
    
    prompt = f"""You are a financial analyst assistant. Answer the user's question using ONLY 
the context provided below. Do not use any outside knowledge.

Context:
{context}

Question: {question}

Rules:
- If the context fully answers the question, answer clearly and cite which 
  source chunk(s) you used.
- If the context only partially answers the question, answer what you can 
  and explicitly state what's missing.
- If the context does not contain relevant information, say exactly: 
  "I cannot answer this from the provided documents."
- Never guess or fill in gaps with general knowledge.

Answer:
"""
    
    # We use gemini-2.5-flash as it is the fastest, smartest model for RAG synthesis available today
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    from retrieval import retrieve
    
    test_question = "What was the company's total revenue?"
    test_collection = "test_docs"
    db_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    print(f"Retrieving context for question: '{test_question}'...")
    
    # 2. Retrieve chunks for the question
    retrieved_chunks = retrieve(test_question, collection_name=test_collection, top_k=5, db_path=db_test_path)
    
    if not retrieved_chunks:
        print("No chunks retrieved. Please ensure you have run embeddings.py to populate ChromaDB.")
    else:
        print(f"\nRetrieved {len(retrieved_chunks)} chunks.")
        print("Sources used:")
        for c in retrieved_chunks:
            print(f"  - {c.get('source')} (Chunk ID: {c.get('chunk_id')})")
            
        print("\nGenerating answer with Gemini...\n")
        print("-" * 50)
        
        # 3. Call generate_answer()
        answer = generate_answer(test_question, retrieved_chunks)
        
        # 4. Print the generated answer
        print(answer)
        print("-" * 50)
