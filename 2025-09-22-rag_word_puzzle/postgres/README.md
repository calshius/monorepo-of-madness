# RAG PostgreSQL Database Setup

This directory contains a Docker Compose setup for a PostgreSQL database with pgvector extension, specifically configured for Retrieval-Augmented Generation (RAG) applications.

## Features

- PostgreSQL 16 with pgvector extension pre-installed
- Pre-configured schema for RAG applications
- Vector similarity search functions
- Sample data for testing
- Persistent data storage

## Quick Start

1. **Start the database:**
   ```bash
   cd postgres
   docker-compose up -d
   ```

2. **Check if it's running:**
   ```bash
   docker-compose ps
   ```

3. **Connect to the database:**
   ```bash
   # Using psql (if installed locally)
   psql -h localhost -U rag_user -d rag_database

   # Or using Docker
   docker-compose exec postgres psql -U rag_user -d rag_database
   ```

4. **Stop the database:**
   ```bash
   docker-compose down
   ```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and modify as needed:

- `POSTGRES_DB`: Database name (default: rag_database)
- `POSTGRES_USER`: Database user (default: rag_user)
- `POSTGRES_PASSWORD`: Database password (default: rag_password)
- `POSTGRES_PORT`: Port to expose (default: 5432)

### Embedding Dimensions

The default schema is configured for OpenAI's text-embedding-ada-002 model (1536 dimensions). If you're using a different embedding model, update the vector dimension in:

1. `init/01-init-rag-schema.sql` - Change `vector(1536)` to your dimension
2. The similarity search function parameter

Common embedding dimensions:
- OpenAI text-embedding-ada-002: 1536
- Sentence Transformers all-MiniLM-L6-v2: 384
- Sentence Transformers all-mpnet-base-v2: 768

## Database Schema

### Tables

#### `rag.documents`
Stores original documents and metadata.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | VARCHAR(500) | Document title |
| content | TEXT | Full document content |
| source | VARCHAR(255) | Source identifier |
| metadata | JSONB | Additional metadata |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `rag.embeddings`
Stores vector embeddings for document chunks.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| document_id | INTEGER | Foreign key to documents |
| chunk_index | INTEGER | Index of chunk within document |
| content | TEXT | Chunk content |
| embedding | vector(1536) | Vector embedding |
| metadata | JSONB | Chunk-specific metadata |
| created_at | TIMESTAMP | Creation timestamp |

### Functions

#### `rag.similarity_search(query_embedding, threshold, limit)`
Performs cosine similarity search on embeddings.

**Parameters:**
- `query_embedding`: vector(1536) - The query embedding
- `similarity_threshold`: float - Minimum similarity score (default: 0.7)
- `match_count`: int - Maximum results to return (default: 10)

**Returns:** Table with id, document_id, content, similarity, metadata

### Views

#### `rag.document_embeddings`
Convenient view joining documents with their embeddings.

## Usage Examples

### Python with psycopg2

```python
import psycopg2
import numpy as np
from psycopg2.extras import register_adapter, Json

# Register numpy array adapter for vectors
register_adapter(np.ndarray, lambda a: a.tolist())

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="rag_database",
    user="rag_user",
    password="rag_password"
)

# Insert a document
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO rag.documents (title, content, source, metadata)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, ("My Document", "Document content here", "api", {"category": "test"}))
    document_id = cur.fetchone()[0]

# Insert an embedding
embedding = np.random.rand(1536).tolist()  # Replace with real embedding
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO rag.embeddings (document_id, content, embedding)
        VALUES (%s, %s, %s)
    """, (document_id, "Chunk content", embedding))

# Search for similar content
query_embedding = np.random.rand(1536).tolist()  # Replace with real query embedding
with conn.cursor() as cur:
    cur.execute("""
        SELECT * FROM rag.similarity_search(%s::vector, 0.5, 5)
    """, (query_embedding,))
    results = cur.fetchall()

conn.commit()
conn.close()
```

### SQL Examples

```sql
-- Insert a document
INSERT INTO rag.documents (title, content, source) 
VALUES ('AI Research Paper', 'This paper discusses...', 'arxiv');

-- Insert an embedding (replace with actual vector)
INSERT INTO rag.embeddings (document_id, content, embedding)
VALUES (1, 'Introduction paragraph', '[0.1, 0.2, ...]'::vector);

-- Perform similarity search
SELECT * FROM rag.similarity_search('[0.1, 0.2, ...]'::vector, 0.7, 10);

-- Get all documents with their embeddings
SELECT * FROM rag.document_embeddings WHERE document_id = 1;
```

## Maintenance

### Backup Database
```bash
docker-compose exec postgres pg_dump -U rag_user rag_database > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U rag_user rag_database < backup.sql
```

### View Logs
```bash
docker-compose logs postgres
```

### Reset Database
```bash
docker-compose down -v  # This will delete all data!
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change `POSTGRES_PORT` in `.env`
2. **Permission denied**: Ensure Docker has proper permissions
3. **Connection refused**: Wait for healthcheck to pass, check with `docker-compose ps`

### Performance Tuning

For large datasets, consider:

1. **Adjusting IVFFlat index parameters:**
   ```sql
   DROP INDEX embeddings_embedding_idx;
   CREATE INDEX embeddings_embedding_idx ON rag.embeddings 
   USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);
   ```

2. **Using HNSW index for better performance:**
   ```sql
   CREATE INDEX embeddings_embedding_hnsw_idx ON rag.embeddings 
   USING hnsw (embedding vector_cosine_ops);
   ```

## Integration with RAG Applications

This setup is designed to work with popular RAG frameworks:

- **LangChain**: Use with `PGVector` vector store
- **LlamaIndex**: Use with `PGVectorStore`
- **Custom implementations**: Use the provided functions and schema

The schema follows common patterns used in RAG applications, making it easy to integrate with existing tools and frameworks.