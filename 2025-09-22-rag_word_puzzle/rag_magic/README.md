# RAG Magic 🧙‍♂️

A powerful CLI tool for Retrieval-Augmented Generation (RAG) operations using PostgreSQL with pgvector and Gemini embeddings.

## Features

- 🗃️ **Document Ingestion**: Chunk and vectorize documents for semantic search
- 🔍 **Intelligent Query**: Ask questions in natural language and get AI-powered answers
- 📊 **Database Management**: List, view, and manage your vectorized documents
- 🔌 **Easy Setup**: Simple configuration with environment variables
- 📦 **Multiple File Types**: Support for text, markdown, code files, and more
- ⚡ **High Performance**: Optimized chunking and batch embedding generation

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Docker (for PostgreSQL database)
- Google Gemini API key

### 2. Setup Database

```bash
# Start the PostgreSQL database with pgvector
cd postgres
./manage.sh start
```

### 3. Install and Configure

```bash
# Install the package
pip install -e .

# Initialize configuration
rag-magic init

# Edit the .env file and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here

# Test the database connection
rag-magic test-connection
```

### 4. Ingest Your First Document

```bash
# Ingest a document
rag-magic ingest path/to/your/document.txt

# List vectorized documents
rag-magic list-documents
```

### 5. Query Your Documents

```bash
# Ask questions about your documents
rag-magic query "What is the main topic of the document?"
```

## Commands

### `rag-magic test-connection`
Test database connectivity and schema validation.

### `rag-magic ingest <file_path>`
Ingest a file by chunking it and creating vector embeddings.

**Options:**
- `--chunk-size, -c`: Chunk size for text splitting (default: 1000)
- `--chunk-overlap, -o`: Overlap between chunks (default: 200)
- `--force, -f`: Overwrite existing document

**Example:**
```bash
rag-magic ingest document.txt --chunk-size 800 --chunk-overlap 100
```

### `rag-magic query <question>`
Query vectorized documents using natural language.

**Options:**
- `--threshold, -t`: Similarity threshold (default: 0.7)
- `--max-results, -n`: Maximum results to return (default: 10)
- `--model, -m`: Chat model to use (default: gpt-3.5-turbo)

**Example:**
```bash
rag-magic query "How does the authentication system work?" --threshold 0.6
```

### `rag-magic list-documents`
List all vectorized documents in the database.

### `rag-magic delete <source>`
Delete a document and its embeddings from the database.

### `rag-magic config`
Display current configuration.

### `rag-magic init`
Initialize configuration by creating a sample .env file.

## Supported File Types

- `.txt` - Plain text files
- `.md` - Markdown files
- `.py` - Python files
- `.js` - JavaScript files
- `.html` - HTML files
- `.css` - CSS files
- `.json` - JSON files
- `.csv` - CSV files
- `.log` - Log files

## Configuration

Create a `.env` file in your project directory:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_database
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

# Gemini Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Model Configuration
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo

# Default Settings
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
DEFAULT_SIMILARITY_THRESHOLD=0.7
DEFAULT_MAX_RESULTS=10
```

## Project Structure

```
rag_magic/
├── src/rag_magic/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # CLI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database operations
│   └── embeddings.py        # Document processing and embeddings
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd rag_magic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run linting
ruff check .
black .
mypy .
```

### Running Tests

```bash
pytest
```

## How It Works

1. **Document Ingestion**: Files are read, chunked into smaller pieces with configurable overlap
2. **Embedding Generation**: Each chunk is converted to a vector embedding using Gemini's API
3. **Storage**: Documents and embeddings are stored in PostgreSQL with pgvector extension
4. **Querying**: User questions are converted to embeddings and similar chunks are found using cosine similarity
5. **Answer Generation**: Retrieved chunks provide context for GPT to generate comprehensive answers

## Performance Tips

- **Chunk Size**: Smaller chunks (500-800 tokens) work better for specific questions, larger chunks (1000-1500) for general topics
- **Overlap**: 10-20% overlap helps maintain context between chunks
- **Similarity Threshold**: Lower thresholds (0.5-0.6) return more results, higher (0.8+) are more precise
- **Batch Processing**: The tool automatically batches embedding requests to optimize API usage

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is running
cd postgres
./manage.sh status

# Restart database
./manage.sh restart

# Check logs
./manage.sh logs
```

### Gemini API Issues
- Verify your API key is correct
- Check your Gemini account has sufficient credits
- Ensure you have access to the embedding model (text-embedding-ada-002)

### Memory Issues
- Reduce chunk size for large documents
- Process files one at a time for very large datasets

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Word Puzzle Tutorial 🧩

Want to test RAG Magic's capabilities in a fun way? Try the hidden word puzzle challenge!

<details>
<summary>🔍 Click here for puzzle hints and tutorial</summary>

### The Challenge
In the `../word_puzzles/` directory, there are 5 mysterious files filled with garbage text and random characters. Hidden within each file is a secret word that, when found in order, spell out a congratulatory message!

### Getting Started
1. First, ingest all the puzzle files:
```bash
cd ../word_puzzles
rag-magic ingest puzzle1_well.txt
rag-magic ingest puzzle2_done.txt
rag-magic ingest puzzle3_you.txt
rag-magic ingest puzzle4_found.txt
rag-magic ingest puzzle5_me.txt
```

2. List your documents to confirm they're all loaded:
```bash
rag-magic list-documents
```

### Strategic Query Approaches
Try these carefully designed queries to discover the hidden words. **Pro Tip**: Use a lower similarity threshold (0.3-0.5) for better results with noisy text!

#### 1. General Discovery Queries
```bash
# Start with broad pattern recognition (use lower threshold for more results)
rag-magic query "Find any complete words that stand out clearly among random characters and noise" --threshold 0.3

# Look for intentional patterns
rag-magic query "Are there any four-letter words that appear to be deliberately placed in these documents?" --threshold 0.4

# Search for the complete sequence
rag-magic query "Find a five-word sequence across these files that forms a congratulatory statement" --threshold 0.3
```

#### 2. Semantic-Based Discovery
```bash
# Look for encouraging/positive words
rag-magic query "What words in these documents relate to success, completion, or achievement?" --threshold 0.4

# Search for discovery-related terms
rag-magic query "Find words that relate to finding, discovering, or locating something" --threshold 0.3

# Look for personal pronouns and references
rag-magic query "What pronouns or personal references can you identify in these texts?" --threshold 0.3
```

#### 3. Targeted Word Hunting
```bash
# Search for specific word patterns
rag-magic query "Find any instances of the word 'well' or words starting with 'w'" --threshold 0.3

# Look for completion words
rag-magic query "Find words that indicate completion or accomplishment like 'done' or 'finished'" --threshold 0.3

# Search for pronouns
rag-magic query "Identify pronouns like 'you' or 'me' hidden in these documents" --threshold 0.3
```

#### 4. File-Specific Queries
```bash
# Target each file individually if needed
rag-magic query "What clear word can be found in puzzle1_well.txt among the random text?" --threshold 0.3 --max-results 5

rag-magic query "What meaningful word stands out in puzzle2_done.txt?" --threshold 0.3 --max-results 5

rag-magic query "Find the hidden word in puzzle3_you.txt that's not random noise" --threshold 0.3 --max-results 5

rag-magic query "What word is deliberately placed in puzzle4_found.txt?" --threshold 0.3 --max-results 5

rag-magic query "Identify the clear word in puzzle5_me.txt among the garbage text" --threshold 0.3 --max-results 5
```

#### 5. Sequence Assembly Queries
```bash
# Try to put it all together
rag-magic query "What five words, when taken in order from puzzle1 through puzzle5, form a complete congratulatory message?" --threshold 0.4

# Validate the sequence
rag-magic query "Do the words 'well', 'done', 'you', 'found', 'me' appear as hidden words across these puzzle files?" --threshold 0.3

# Semantic validation
rag-magic query "What does the phrase formed by the hidden words in these puzzles mean?" --threshold 0.4
```

#### 🎯 Query Tuning Tips
- **Lower Threshold (0.3-0.5)**: Use for noisy text with hidden patterns
- **Higher Max Results (15-20)**: Get more context when searching in garbage text
- **Combine Parameters**: `--threshold 0.3 --max-results 15` for comprehensive searches

### The Learning Experience
This puzzle demonstrates:
- **Semantic vs. Keyword Search**: RAG finds meaning even in noisy text
- **Chunking Strategy**: How RAG handles mixed meaningful and garbage content  
- **Vector Similarity**: Why embeddings work better than simple text matching
- **Context Understanding**: How AI can find patterns humans might miss

### Solution Validation
Once you think you've found all the words, try:
```bash
rag-magic query "What complete message do the hidden words spell out?"
rag-magic query "Put the discovered words in order to form a sentence"
```

**Pro Tip**: The files are numbered in the order the words should appear! 📝

Good luck, and may your RAG skills be sharp! ✨

</details>

## Support

For issues and questions:
- Check the troubleshooting section
- Review the database setup in `postgres/README.md`
- Open an issue on GitHub
