import os
import json
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def verify_answer(question: str, chunks: list, draft_answer: str) -> dict:
    """
    Verifies if the AI's draft answer is supported by the context chunks.
    Returns a dictionary parsed from the LLM's JSON output.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")
        
    context_parts = []
    for c in chunks:
        source = c.get("source", "Unknown Source")
        chunk_id = c.get("chunk_id", "Unknown ID")
        text = c.get("text", "")
        context_parts.append(f"[Source: {source}, Chunk ID: {chunk_id}]\n{text}")
        
    context = "\n\n".join(context_parts)
    
    prompt = f"""You are a strict fact-checker. Your job is to determine whether an AI-generated 
answer is actually supported by the source context, or whether it contains 
unsupported claims (hallucination).

Context:
{context}

Question: {question}

AI's Answer: {draft_answer}

Carefully check each factual claim in the AI's answer against the context. 
Respond ONLY in this exact JSON format, nothing else:

{{
  "supported": true or false,
  "confidence": 0-100,
  "unsupported_claims": ["list any specific claims not backed by context, empty list if none"],
  "reasoning": "1-2 sentence explanation of your judgment"
}}"""

    # We use gemini-2.5-flash as the fast verification judge
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    # Configure generation to enforce JSON output so it is reliably parseable
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json"
    )
    
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    
    # Parse the response text as JSON and return the dictionary
    return json.loads(response.text)

if __name__ == "__main__":
    from retrieval import retrieve
    from answerer import generate_answer
    
    test_collection = "test_docs"
    db_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    questions = [
        {
            "label": "Question A (Covered by docs)",
            "query": "What was the company's total revenue?"
        },
        {
            "label": "Question B (Unrelated/Not covered)",
            "query": "What was Apple's total revenue last year?"
        }
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"--- {q['label']} ---")
        print(f"Question: '{q['query']}'")
        
        # 1. Retrieve
        print("\n[1/3] Retrieving chunks...")
        chunks = retrieve(q['query'], collection_name=test_collection, top_k=5, db_path=db_test_path)
        print(f"Retrieved {len(chunks)} chunks.")
        
        if not chunks:
            print("Skipping verification because no chunks were retrieved.")
            continue
            
        # 2. Generate Answer
        print("\n[2/3] Generating draft answer...")
        draft_answer = generate_answer(q['query'], chunks)
        print(f"\n>>> Draft Answer:\n{draft_answer}\n")
        
        # 3. Verify
        print("[3/3] Verifying answer against source chunks...")
        verification_result = verify_answer(q['query'], chunks, draft_answer)
        
        print("\n>>> Verifier JSON Output:")
        print(json.dumps(verification_result, indent=2))
        print(f"{'='*60}\n")