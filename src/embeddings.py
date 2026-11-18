import os
# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure Google Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Helper function with retry logic to get embeddings for a batch of texts.
    """
    response = genai.embed_content(
        model="models/gemini-embedding-2",
        content=texts,
        task_type="retrieval_document"
    )
    return response['embedding']

def embed_and_store(chunks: List[Dict], collection_name: str, db_path: str = "./chroma_db"):
    """
    Embeds chunk text using Gemini and stores them in a local ChromaDB collection.
    """
    if not chunks:
        print("No chunks provided to embed.")
        return None
        
    # Ensure api key is configured
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in the environment.")

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=db_path)
    
    # Get or create collection
    collection = client.get_or_create_collection(name=collection_name)
    
    print(f"Embedding {len(chunks)} chunks and storing in '{collection_name}' collection...")
    
    # Process in batches to avoid payload size limits and handle rate limiting gracefully
    batch_size = 15
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch_chunks]
        
        batch_ids = [f"{c['source']}_{c['chunk_id']}" for c in batch_chunks]
        
        # Check if these chunks are already in the database to save API quota
        existing = collection.get(ids=batch_ids)
        if existing and len(existing['ids']) == len(batch_ids):
            print(f"Skipping {len(batch_ids)} chunks (already embedded).")
            continue

        try:
            batch_embeddings = get_embeddings_batch(texts)
        except Exception as e:
            print(f"Error during embedding generation: {e}")
            raise
            
        batch_metadatas = [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in batch_chunks]
        
        # Add to collection using upsert to avoid errors on duplicates
        collection.upsert(
            embeddings=batch_embeddings,
            documents=texts,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"Stored {i + len(batch_chunks)} / {len(chunks)} chunks in ChromaDB.")
        
        # Sleep to stay within the free-tier API rate limits (Google restricts to 15 RPM for free tier)
        if i + batch_size < len(chunks):
            import time
            print("Sleeping for 15 seconds to respect free-tier API rate limits...")
            time.sleep(15)
        
    return collection

if __name__ == "__main__":
    import glob
    from chunking import chunk_pdf
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found. Please add a PDF to the '{data_dir}' directory to run ingestion.")
    else:
        test_collection_name = "test_docs"
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
        
        for pdf_path in pdf_files:
            print(f"\nProcessing {pdf_path}...")
            
            # Get chunks
            chunks = chunk_pdf(pdf_path, chunk_size=800, overlap=100)
            print(f"Extracted {len(chunks)} chunks.")
            
            if chunks:
                # Embed and store (now uses upsert, so running it on the same file is safe)
                collection = embed_and_store(chunks, test_collection_name, db_path=db_path)
                print(f"SUCCESS: Finished processing {os.path.basename(pdf_path)}")
