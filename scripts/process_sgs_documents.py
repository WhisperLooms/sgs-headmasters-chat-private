import os
import json
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='document_processing.log'
)

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

def process_document(file_path: str) -> List[Dict[str, Any]]:
    """Process a document and return chunks with embeddings."""
    try:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings()
        
        processed_chunks = []
        for chunk in chunks:
            embedding = embeddings.embed_query(chunk.page_content)
            processed_chunks.append({
                'content': chunk.page_content,
                'embedding': embedding,
                'metadata': chunk.metadata
            })
        
        return processed_chunks
    
    except Exception as e:
        logging.error(f"Error processing document {file_path}: {str(e)}")
        raise

def store_in_supabase(chunks: List[Dict[str, Any]], document_type: str) -> None:
    """Store processed chunks in Supabase."""
    try:
        for chunk in chunks:
            data = {
                'content': chunk['content'],
                'embedding': chunk['embedding'],
                'metadata': json.dumps(chunk['metadata']),
                'document_type': document_type
            }
            
            result = supabase.table('documents').insert(data).execute()
            if hasattr(result, 'error') and result.error is not None:
                logging.error(f"Error inserting chunk: {result.error}")
    
    except Exception as e:
        logging.error(f"Error storing chunks in Supabase: {str(e)}")
        raise

def main():
    """Main function to process documents and store them in Supabase."""
    try:
        # Process historical documents
        historical_docs_dir = 'SGS_History'
        for filename in os.listdir(historical_docs_dir):
            if filename.endswith(('.pdf', '.txt')):
                file_path = os.path.join(historical_docs_dir, filename)
                logging.info(f"Processing historical document: {filename}")
                chunks = process_document(file_path)
                store_in_supabase(chunks, 'historical')
        
        # Process headmaster documents
        headmaster_docs_dir = 'SGS_Docs-Embedding'
        for filename in os.listdir(headmaster_docs_dir):
            if filename.endswith(('.pdf', '.txt')):
                file_path = os.path.join(headmaster_docs_dir, filename)
                logging.info(f"Processing headmaster document: {filename}")
                chunks = process_document(file_path)
                store_in_supabase(chunks, 'headmaster')
        
        logging.info("Document processing completed successfully")
    
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main()