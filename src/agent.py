import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv
import time
from tenacity import retry, stop_after_attempt, wait_exponential

from retrieval import retrieve
from answerer import generate_answer
from verifier import verify_answer

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=15, max=60))
def reformulate_query(question: str) -> str:
    """
    Calls Gemini to reformulate the query into a broader or differently-worded query.
    """
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    prompt = f"""You are an expert search query reformulator. 
The following question did not return confident results from our document database.
Please rewrite or broaden the question slightly using different keywords so we can try searching again.
Output ONLY the new question, nothing else.

Original question: {question}
New question:"""
    response = model.generate_content(prompt)
    return response.text.strip()

def answer_question(question: str, collection_name: str, max_retries: int = 2, db_path: str = "./chroma_db") -> dict:
    attempt = 0
    trace = []
    current_query = question
    
    while attempt <= max_retries:
        print(f"  [Attempt {attempt}] Query: '{current_query}'")
        
        # 2. Retrieve chunks
        chunks = retrieve(current_query, collection_name=collection_name, top_k=5, db_path=db_path)
        
        # 3. Generate draft answer
        draft_answer = generate_answer(current_query, chunks)
        
        # 4. Verify
        result = verify_answer(current_query, chunks, draft_answer)
        
        confidence = result.get("confidence", 0)
        supported = result.get("supported", False)
        
        # 5. Append to trace
        trace.append({
            "attempt": attempt,
            "query_used": current_query,
            "confidence": confidence,
            "supported": supported
        })
        
        # Extract unique sources
        unique_sources = list(set([c.get("source") for c in chunks if c.get("source")]))
        
        # If the answerer explicitly states it cannot answer, we must force a retry 
        # because the verifier will say it is "100% confident" that it cannot answer.
        if "I cannot answer this from the provided documents" in draft_answer:
            confidence = 0 
            
        # 6. If confident
        if confidence >= 70 and supported:
            return {
                "final_answer": draft_answer,
                "confidence": confidence,
                "sources": unique_sources,
                "trace": trace,
                "status": "confident"
            }
            
        # 7. If confidence < 70 and attempt < max_retries
        if attempt < max_retries:
            print(f"  [Attempt {attempt}] Low confidence ({confidence}%). Reformulating query...")
            current_query = reformulate_query(current_query)
            attempt += 1
        else:
            break
            
    # 8. If max_retries exhausted and still not confident
    return {
        "final_answer": "I don't have reliable information to answer this confidently based on the available documents.",
        "confidence": confidence,
        "low_confidence_draft": draft_answer,
        "reasoning": result.get("reasoning", ""),
        "trace": trace,
        "status": "refused"
    }

if __name__ == "__main__":
    import json
    
    test_collection = "test_docs"
    db_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    questions = [
        {
            "label": "Question A (Succeeds first attempt)",
            "query": "What was the company's total revenue?"
        },
        {
            "label": "Question B (Needs retry - vaguely worded)",
            "query": "What numbers did they make last year?"
        },
        {
            "label": "Question C (Exhausts retries - completely unrelated)",
            "query": "What are the names of the CEO's pets?"
        }
    ]
    
    for q in questions:
        print(f"\n{'='*70}")
        print(f"--- {q['label']} ---")
        print(f"Original Question: '{q['query']}'")
        print("Running Agent Flow...\n")
        
        result = answer_question(q['query'], test_collection, max_retries=2, db_path=db_test_path)
        
        print("\n>>> FINAL AGENT RESULT <<<")
        print(json.dumps(result, indent=2))
        print(f"{'='*70}\n")
        
        print("Waiting 60 seconds to respect Gemini Free Tier API limits before the next question...")
        time.sleep(60)
