import os
# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

def retrieve(query: str, collection_name: str, top_k: int = 5, db_path: str = "./chroma_db"):
    """
    Retrieves the top_k most relevant chunks for a given query from ChromaDB.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set. Please set it in your .env file.")

    # 1. Embed the query using the same model as our document chunks
    try:
        response = genai.embed_content(
            model="models/gemini-embedding-2",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = response['embedding']
    except Exception as e:
        print(f"Error embedding query: {e}")
        return []
        
    # 2. Connect to ChromaDB and grab our collection
    client = chromadb.PersistentClient(path=db_path)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"Error accessing collection '{collection_name}'. Make sure you ran embeddings.py first! Details: {e}")
        return []
        
    # 3. Search the vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # 4. Format the raw ChromaDB results into an easy-to-use list of dictionaries
    formatted_results = []
    if results and 'documents' in results and results['documents'][0]:
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "text": results['documents'][0][i],
                "source": results['metadatas'][0][i].get("source", "Unknown") if results['metadatas'] else "Unknown",
                "chunk_id": results['metadatas'][0][i].get("chunk_id", -1) if results['metadatas'] else -1,
                "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else None
            })
            
    return formatted_results

if __name__ == "__main__":
    # Test our retrieval logic
    test_collection = "test_docs"
    db_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    # Interactive prompt so you can ask queries dynamically!
    print("\n--- Welcome to the Trust RAG Search ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        test_query = input("Ask a question about the report: ")
        
        if test_query.lower() in ['exit', 'quit']:
            print("Exiting search...")
            break
            
        if not test_query.strip():
            continue
            
        print(f"\nSearching for: '{test_query}' in '{test_collection}'...")
        
        results = retrieve(test_query, collection_name=test_collection, top_k=3, db_path=db_test_path)
        
        if not results:
            print("No results found. Did you run embeddings.py first?\n")
        else:
            for i, res in enumerate(results):
                distance = res['distance'] if res['distance'] is not None else 0.0
                print(f"\n--- Result {i+1} (Distance Score: {distance:.4f}) ---")
                print(f"Source: {res['source']} (Chunk ID: {res['chunk_id']})")
                
                # Clean up the text snippet to be on one line for easier reading
                snippet = res['text'].replace('\n', ' ')
                print(f"Text Snippet: {snippet[:250]}...")
                
        print("\n" + "-" * 60 + "\n")
