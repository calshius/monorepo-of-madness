"""Document processing and embedding generation for RAG Magic."""

import os
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DocumentProcessor:
    """Handles document chunking and embedding generation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "models/text-embedding-004"
    ):
        """Initialize with Google Gemini API key and embedding model."""
        self.api_key = (
            api_key or os.getenv("GEMINI_TOKEN") or os.getenv("GOOGLE_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GEMINI_TOKEN or GOOGLE_API_KEY environment variable."
            )

        self.model = model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model, google_api_key=self.api_key
        )

    def read_file(self, file_path: str) -> str:
        """Read and return file contents."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            console.print(
                f"[green]✓ Read file: {path.name} ({len(content)} characters)[/green]"
            )
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()
                console.print(
                    f"[yellow]⚠ Read file with latin-1 encoding: {path.name}[/yellow]"
                )
                return content
            except Exception as e:
                raise ValueError(f"Could not read file {file_path}: {e}")

    def chunk_text(
        self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate end position
            end = start + chunk_size

            # If this is not the last chunk, try to break at word boundary
            if end < text_length:
                # Look for the last space within the chunk
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position, accounting for overlap
            start = end - chunk_overlap
            if start <= 0:
                start = end

        console.print(f"[blue]✓ Split text into {len(chunks)} chunks[/blue]")
        return chunks

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation for Gemini)."""
        # Rough approximation: ~4 characters per token for English text
        return len(text) // 4

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Google Gemini."""
        if not texts:
            return []

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Generating embeddings for {len(texts)} chunks...", total=None
                )

                # Generate embeddings using LangChain
                embeddings = self.embeddings.embed_documents(texts)

                progress.update(task, completed=True)
                console.print(
                    f"[green]✓ Generated {len(embeddings)} embeddings[/green]"
                )

                return embeddings

        except Exception as e:
            console.print(f"[red]✗ Error generating embeddings: {e}[/red]")
            raise

    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            console.print(f"[red]✗ Error generating embedding: {e}[/red]")
            raise

    def process_file(
        self, file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[Tuple[str, List[float]]]:
        """Process a file: read, chunk, and generate embeddings."""
        console.print(f"[blue]Processing file: {file_path}[/blue]")

        # Read file
        content = self.read_file(file_path)

        # Chunk text
        chunks = self.chunk_text(content, chunk_size, chunk_overlap)

        if not chunks:
            console.print("[yellow]⚠ No chunks generated from file[/yellow]")
            return []

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        # Combine chunks and embeddings
        result = list(zip(chunks, embeddings))

        console.print(
            f"[green]✓ Processed {file_path}: "
            f"{len(result)} chunk-embedding pairs[/green]"
        )

        return result

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from this model."""
        # Google text-embedding-004 produces 768-dimensional embeddings
        return 768

    def validate_api_connection(self) -> bool:
        """Test the API connection by generating a test embedding."""
        try:
            test_embedding = self.generate_single_embedding("test")
            if test_embedding and len(test_embedding) == self.get_embedding_dimension():
                console.print("[green]✓ Google Gemini API connection validated[/green]")
                return True
            else:
                console.print("[red]✗ Invalid embedding response[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ API connection failed: {e}[/red]")
            return False


def create_processor(
    api_key: Optional[str] = None, model: str = "models/text-embedding-004"
) -> DocumentProcessor:
    """Create and return a DocumentProcessor instance."""
    return DocumentProcessor(api_key=api_key, model=model)
