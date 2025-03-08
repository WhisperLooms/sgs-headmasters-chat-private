import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_supabase():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Create tables
    create_tables(supabase)
    
    # Enable pgvector extension
    enable_pgvector(supabase)
    
    # Create indexes
    create_indexes(supabase)
    
    return supabase

def create_tables(supabase):
    # Documents table
    supabase.table('documents').create({
        'id': 'uuid DEFAULT uuid_generate_v4() PRIMARY KEY',
        'content': 'text NOT NULL',
        'embedding': 'vector(1536)',
        'metadata': 'jsonb',
        'document_type': 'text NOT NULL',
        'created_at': 'timestamptz DEFAULT now()'
    })
    
    # Chat history table
    supabase.table('chat_history').create({
        'id': 'uuid DEFAULT uuid_generate_v4() PRIMARY KEY',
        'session_id': 'uuid NOT NULL',
        'role': 'text NOT NULL',
        'content': 'text NOT NULL',
        'created_at': 'timestamptz DEFAULT now()'
    })
    
    # User sessions table
    supabase.table('user_sessions').create({
        'id': 'uuid DEFAULT uuid_generate_v4() PRIMARY KEY',
        'user_id': 'uuid',
        'created_at': 'timestamptz DEFAULT now()'
    })

def enable_pgvector(supabase):
    supabase.query("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)

def create_indexes(supabase):
    # Create index on embeddings
    supabase.query("""
        CREATE INDEX ON documents
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    
    # Create index on document type
    supabase.query("""
        CREATE INDEX ON documents (document_type);
    """)
    
    # Create index on chat history session_id
    supabase.query("""
        CREATE INDEX ON chat_history (session_id);
    """)

if __name__ == "__main__":
    setup_supabase()