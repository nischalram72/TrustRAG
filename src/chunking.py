import os
# pyrefly: ignore [missing-import]
from pypdf import PdfReader

def chunk_pdf(pdf_path, chunk_size=800, overlap=100):
    """
    Extracts text from a PDF and splits it into overlapping chunks of roughly chunk_size characters.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    chunks = []
    source = os.path.basename(pdf_path)
    
    start = 0
    chunk_id = 0
    text_length = len(full_text)
    
    while start < text_length:
        end = start + chunk_size
        chunk_text = full_text[start:end].strip()
        
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_id": chunk_id
            })
            chunk_id += 1
            
        if start + chunk_size >= text_length:
            break
            
        start += chunk_size - overlap
        
    return chunks

if __name__ == "__main__":
    import glob
    
    # Find any PDF in the data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"Test skipped: Please add a PDF to the '{data_dir}' directory to run this test.")
    else:
        sample_pdf = pdf_files[0]
        print(f"Processing {sample_pdf}...")
        chunks = chunk_pdf(sample_pdf)
        print(f"Total chunks extracted: {len(chunks)}")
        print("\n--- First 2 Chunks ---")
        for chunk in chunks[:2]:
            print(chunk)
