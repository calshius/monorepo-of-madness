"""RAG Magic CLI - A tool for RAG operations with PostgreSQL and vector embeddings."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import create_sample_env_file, get_config
from .database import DatabaseConnection, display_documents_table
from .embeddings import DocumentProcessor

app = typer.Typer(
    name="rag-magic",
    help="A CLI tool for RAG operations with PostgreSQL and vector embeddings",
    add_completion=False,
)

console = Console()


def is_supported_file(file_path: str) -> bool:
    """Check if file type is supported."""
    path = Path(file_path)
    supported_extensions = [
        ".txt",
        ".md",
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".csv",
        ".log",
    ]
    return path.suffix.lower() in supported_extensions


def get_file_title(file_path: str) -> str:
    """Extract a reasonable title from file path."""
    path = Path(file_path)
    title = path.stem
    title = title.replace("_", " ").replace("-", " ")
    title = " ".join(word.capitalize() for word in title.split())
    return title


@app.command()
def test_connection():
    """Test database connectivity and schema."""
    config = get_config()
    if not config.validate():
        raise typer.Exit(1)

    db = DatabaseConnection.from_env()
    success = db.test_connection()

    if not success:
        console.print("[red]Database connection test failed![/red]")
        raise typer.Exit(1)

    console.print("[green]✅ Database connection test passed![/green]")


@app.command()
def ingest(
    file_path: str = typer.Argument(..., help="Path to the file to ingest"),
    chunk_size: Optional[int] = typer.Option(
        None, "--chunk-size", "-c", help="Chunk size for text splitting"
    ),
    chunk_overlap: Optional[int] = typer.Option(
        None, "--chunk-overlap", "-o", help="Overlap between chunks"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing document"
    ),
):
    """Ingest a file: chunk it and create embeddings, then store in database."""
    config = get_config()
    if not config.validate():
        raise typer.Exit(1)

    # Check if file exists and is supported
    if not Path(file_path).exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    if not is_supported_file(file_path):
        console.print(f"[red]Unsupported file type: {file_path}[/red]")
        console.print(
            "Supported extensions: .txt, .md, .py, .js, .html, .css, .json, .csv, .log"
        )
        raise typer.Exit(1)

    # Use config defaults if not specified
    chunk_size = chunk_size or config.default_chunk_size
    chunk_overlap = chunk_overlap or config.default_chunk_overlap

    # Check if document already exists
    db = DatabaseConnection.from_env()
    if not db.connect():
        raise typer.Exit(1)

    existing_doc = db.get_document_by_source(file_path)
    if existing_doc and not force:
        console.print(f"[yellow]Document already exists: {file_path}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Delete existing document if force is used
    if existing_doc and force:
        db.delete_document_by_source(file_path)

    # Process file
    try:
        processor = DocumentProcessor()
        chunk_embedding_pairs = processor.process_file(
            file_path, chunk_size, chunk_overlap
        )

        if not chunk_embedding_pairs:
            console.print("[yellow]No content to process[/yellow]")
            raise typer.Exit(1)

        # Extract chunks and embeddings from the pairs
        chunks = [pair[0] for pair in chunk_embedding_pairs]
        embeddings = [pair[1] for pair in chunk_embedding_pairs]

        # Store in database
        title = get_file_title(file_path)
        # Read the content again for metadata (since we need the full content)
        content = processor.read_file(file_path)
        metadata = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "total_chunks": len(chunks),
        }

        document_id = db.insert_document(title, content, file_path, metadata)
        if not document_id:
            console.print("[red]Failed to insert document[/red]")
            raise typer.Exit(1)

        # Insert embeddings
        success_count = 0
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_metadata = {"chunk_size": len(chunk)}
            if db.insert_embedding(document_id, i, chunk, embedding, chunk_metadata):
                success_count += 1

        console.print(f"[green]✅ Successfully ingested document:[/green]")
        console.print(f"  Document ID: {document_id}")
        console.print(f"  Title: {title}")
        console.print(f"  Chunks: {success_count}/{len(chunks)}")

    except Exception as e:
        console.print(f"[red]Error processing file: {e}[/red]")
        raise typer.Exit(1)
    finally:
        db.disconnect()


@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask"),
    threshold: Optional[float] = typer.Option(
        None, "--threshold", "-t", help="Similarity threshold"
    ),
    max_results: Optional[int] = typer.Option(
        None, "--max-results", "-n", help="Maximum results to return"
    ),
    chat_model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Chat model to use"
    ),
):
    """Query the vectorized documents using natural language."""
    config = get_config()
    if not config.validate():
        raise typer.Exit(1)

    # Use config defaults if not specified
    threshold = threshold or config.default_similarity_threshold
    max_results = max_results or config.default_max_results
    chat_model = chat_model or config.chat_model

    try:
        processor = DocumentProcessor()
        db = DatabaseConnection.from_env()

        if not db.connect():
            raise typer.Exit(1)

        # Generate embedding for the question
        console.print("[blue]🔍 Searching for relevant content...[/blue]")
        question_embedding = processor.generate_single_embedding(question)

        # Search for similar content
        results = db.similarity_search(question_embedding, threshold, max_results)

        if not results:
            console.print(
                "[yellow]No relevant content found. Try lowering the threshold.[/yellow]"
            )
            raise typer.Exit(0)

        # Display search results
        console.print(f"[green]Found {len(results)} relevant chunks:[/green]")

        context_chunks = []
        for i, result in enumerate(results, 1):
            similarity = result["similarity"]
            content = (
                result["content"][:200] + "..."
                if len(result["content"]) > 200
                else result["content"]
            )

            console.print(f"\n[cyan]Result {i} (similarity: {similarity:.3f}):[/cyan]")
            console.print(f"[dim]{content}[/dim]")

            context_chunks.append(result["content"])

        # Generate answer using Google Gemini
        console.print(f"\n[blue]🤖 Generating answer using {chat_model}...[/blue]")

        context = "\n\n".join(context_chunks)
        prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""

        from langchain_google_genai import ChatGoogleGenerativeAI

        chat = ChatGoogleGenerativeAI(
            model=chat_model,
            google_api_key=config.gemini_api_key,
            temperature=0.7,
            max_output_tokens=500,
        )

        response = chat.invoke(prompt)
        answer = response.content

        # Display answer in a panel
        console.print(Panel(answer, title="🤖 Answer", border_style="green"))

    except Exception as e:
        console.print(f"[red]Error during query: {e}[/red]")
        raise typer.Exit(1)
    finally:
        if "db" in locals():
            db.disconnect()


@app.command()
def list_documents():
    """List all vectorized documents in the database."""
    config = get_config()
    if not config.validate():
        raise typer.Exit(1)

    try:
        db = DatabaseConnection.from_env()
        if not db.connect():
            raise typer.Exit(1)

        documents = db.get_documents()
        display_documents_table(documents)

        if documents:
            total_chunks = sum(doc["chunk_count"] for doc in documents)
            console.print(
                f"\n[blue]Total: {len(documents)} documents, {total_chunks} chunks[/blue]"
            )

    except Exception as e:
        console.print(f"[red]Error listing documents: {e}[/red]")
        raise typer.Exit(1)
    finally:
        if "db" in locals():
            db.disconnect()


@app.command()
def delete(
    source: str = typer.Argument(..., help="Source path of the document to delete"),
):
    """Delete a document and its embeddings from the database."""
    config = get_config()
    if not config.validate():
        raise typer.Exit(1)

    try:
        db = DatabaseConnection.from_env()
        if not db.connect():
            raise typer.Exit(1)

        # Check if document exists
        doc = db.get_document_by_source(source)
        if not doc:
            console.print(f"[yellow]No document found with source: {source}[/yellow]")
            raise typer.Exit(0)

        # Confirm deletion
        console.print(f"[yellow]Delete document: {doc['title']} ({source})?[/yellow]")
        if not typer.confirm("Are you sure?"):
            console.print("Deletion cancelled.")
            raise typer.Exit(0)

        # Delete document
        if db.delete_document_by_source(source):
            console.print("[green]✅ Document deleted successfully[/green]")
        else:
            console.print("[red]Failed to delete document[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error deleting document: {e}[/red]")
        raise typer.Exit(1)
    finally:
        if "db" in locals():
            db.disconnect()


@app.command()
def config():
    """Display current configuration."""
    config_obj = get_config()
    config_obj.display()


@app.command()
def init():
    """Initialize configuration by creating a sample .env file."""
    if create_sample_env_file():
        console.print("\n[green]Next steps:[/green]")
        console.print("1. Edit the .env file and add your Google Gemini API key")
        console.print("2. Start the PostgreSQL database (see postgres/README.md)")
        console.print("3. Test the connection: rag-magic test-connection")
        console.print("4. Ingest a document: rag-magic ingest path/to/file.txt")


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
