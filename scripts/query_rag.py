import os
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_rag_chain():
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Create vector store
    vector_store = SupabaseVectorStore(
        client=supabase,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )
    
    # Initialize language model
    llm = OpenAI(
        temperature=0.7,
        model_name="gpt-4-turbo-preview"
    )
    
    # Set up memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create RAG chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True
    )
    
    return chain

def query_chain(chain, query: str) -> Dict:
    try:
        result = chain({"question": query})
        return {
            "answer": result["answer"],
            "sources": [doc.metadata for doc in result["source_documents"]]
        }
    except Exception as e:
        print(f"Error querying chain: {str(e)}")
        return {
            "answer": "I apologize, but I encountered an error processing your request.",
            "sources": []
        }

if __name__ == "__main__":
    chain = setup_rag_chain()
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        result = query_chain(chain, query)
        print(f"\nAnswer: {result['answer']}")
        print("\nSources:")
        for source in result['sources']:
            print(f"- {source}")