-- Initialize database for RAG applications with pgvector support
-- This script runs automatically when the container starts

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a schema for RAG-related tables
CREATE SCHEMA IF NOT EXISTS rag;

-- Create documents table to store original documents
CREATE TABLE IF NOT EXISTS rag.documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT NOT NULL,
    source VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create embeddings table to store vector embeddings
CREATE TABLE IF NOT EXISTS rag.embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES rag.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER DEFAULT 0,
    content TEXT NOT NULL,
    embedding vector(768), -- Gemini text-embedding-004 dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON rag.embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create index for document lookups
CREATE INDEX IF NOT EXISTS embeddings_document_id_idx ON rag.embeddings(document_id);
CREATE INDEX IF NOT EXISTS documents_source_idx ON rag.documents(source);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION rag.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON rag.documents
    FOR EACH ROW EXECUTE FUNCTION rag.update_updated_at_column();

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION rag.similarity_search(
    query_embedding vector(768),
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    document_id int,
    content text,
    similarity float,
    metadata jsonb
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.document_id,
        e.content,
        1 - (e.embedding <=> query_embedding) AS similarity,
        e.metadata
    FROM rag.embeddings e
    WHERE 1 - (e.embedding <=> query_embedding) > similarity_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Create a view for easy document and embedding joins
CREATE OR REPLACE VIEW rag.document_embeddings AS
SELECT 
    d.id as document_id,
    d.title,
    d.source,
    d.metadata as document_metadata,
    e.id as embedding_id,
    e.chunk_index,
    e.content as chunk_content,
    e.embedding,
    e.metadata as chunk_metadata,
    e.created_at as embedding_created_at
FROM rag.documents d
LEFT JOIN rag.embeddings e ON d.id = e.document_id;

-- Grant permissions (adjust as needed for your security requirements)
GRANT USAGE ON SCHEMA rag TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA rag TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA rag TO PUBLIC;

-- Print confirmation
\echo 'RAG database schema initialized successfully!'
\echo 'Available tables:'
\echo '- rag.documents: Store original documents'
\echo '- rag.embeddings: Store vector embeddings'
\echo 'Available functions:'
\echo '- rag.similarity_search(vector, threshold, limit): Perform similarity search'
\echo 'Available views:'
\echo '- rag.document_embeddings: Join documents with their embeddings'