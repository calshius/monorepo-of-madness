"""Database connection and utilities for RAG Magic."""

import os
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor
from rich.console import Console
from rich.table import Table

console = Console()


class DatabaseConnection:
    """Handles PostgreSQL database connections and operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "rag_database",
        user: str = "rag_user",
        password: str = "rag_password",
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection = None

    @classmethod
    def from_env(cls) -> "DatabaseConnection":
        """Create database connection from environment variables."""
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "rag_database"),
            user=os.getenv("POSTGRES_USER", "rag_user"),
            password=os.getenv("POSTGRES_PASSWORD", "rag_password"),
        )

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor,
            )
            return True
        except psycopg2.Error as e:
            console.print(f"[red]Database connection failed: {e}[/red]")
            return False

    def disconnect(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def test_connection(self) -> bool:
        """Test database connectivity and schema."""
        if not self.connect():
            return False

        try:
            with self._connection.cursor() as cursor:
                # Test basic connectivity
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                console.print(
                    f"[green]✓ Connected to PostgreSQL: {version['version']}[/green]"
                )

                # Test pgvector extension
                cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                if cursor.fetchone():
                    console.print("[green]✓ pgvector extension is installed[/green]")
                else:
                    console.print("[red]✗ pgvector extension not found[/red]")
                    return False

                # Test schema existence
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name = 'rag';"
                )
                if cursor.fetchone():
                    console.print("[green]✓ RAG schema exists[/green]")
                else:
                    console.print("[red]✗ RAG schema not found[/red]")
                    return False

                # Test tables
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'rag' AND table_name IN ('documents', 'embeddings');
                """)
                tables = [row["table_name"] for row in cursor.fetchall()]
                if "documents" in tables and "embeddings" in tables:
                    console.print("[green]✓ Required tables exist[/green]")
                else:
                    console.print(f"[red]✗ Missing tables. Found: {tables}[/red]")
                    return False

                console.print("[green]✓ Database is ready for RAG operations[/green]")
                return True

        except psycopg2.Error as e:
            console.print(f"[red]Database test failed: {e}[/red]")
            return False
        finally:
            self.disconnect()

    def insert_document(
        self,
        title: str,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """Insert a document and return its ID."""
        if not self._connection:
            if not self.connect():
                return None

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rag.documents (title, content, source, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (title, content, source, Json(metadata or {})),
                )

                document_id = cursor.fetchone()["id"]
                self._connection.commit()
                return document_id

        except psycopg2.Error as e:
            console.print(f"[red]Failed to insert document: {e}[/red]")
            self._connection.rollback()
            return None

    def insert_embedding(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Insert an embedding for a document chunk."""
        if not self._connection:
            if not self.connect():
                return False

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rag.embeddings (document_id, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        document_id,
                        chunk_index,
                        content,
                        embedding,
                        Json(metadata or {}),
                    ),
                )

                self._connection.commit()
                return True

        except psycopg2.Error as e:
            console.print(f"[red]Failed to insert embedding: {e}[/red]")
            self._connection.rollback()
            return False

    def similarity_search(
        self, query_embedding: List[float], threshold: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform similarity search on embeddings."""
        if not self._connection:
            if not self.connect():
                return []

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM rag.similarity_search(%s::vector, %s, %s)
                """,
                    (query_embedding, threshold, limit),
                )

                results = cursor.fetchall()
                return [dict(row) for row in results]

        except psycopg2.Error as e:
            console.print(f"[red]Similarity search failed: {e}[/red]")
            return []

    def get_documents(self) -> List[Dict[str, Any]]:
        """Get all documents with basic statistics."""
        if not self._connection:
            if not self.connect():
                return []

        try:
            with self._connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        d.id,
                        d.title,
                        d.source,
                        d.created_at,
                        d.metadata,
                        COUNT(e.id) as chunk_count
                    FROM rag.documents d
                    LEFT JOIN rag.embeddings e ON d.id = e.document_id
                    GROUP BY d.id, d.title, d.source, d.created_at, d.metadata
                    ORDER BY d.created_at DESC
                """)

                results = cursor.fetchall()
                return [dict(row) for row in results]

        except psycopg2.Error as e:
            console.print(f"[red]Failed to get documents: {e}[/red]")
            return []

    def get_document_by_source(self, source: str) -> Optional[Dict[str, Any]]:
        """Get a document by its source."""
        if not self._connection:
            if not self.connect():
                return None

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM rag.documents WHERE source = %s
                """,
                    (source,),
                )

                result = cursor.fetchone()
                return dict(result) if result else None

        except psycopg2.Error as e:
            console.print(f"[red]Failed to get document: {e}[/red]")
            return None

    def delete_document_by_source(self, source: str) -> bool:
        """Delete a document and its embeddings by source."""
        if not self._connection:
            if not self.connect():
                return False

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM rag.documents WHERE source = %s
                """,
                    (source,),
                )

                deleted_count = cursor.rowcount
                self._connection.commit()

                if deleted_count > 0:
                    console.print(f"[green]Deleted document: {source}[/green]")
                    return True
                else:
                    console.print(
                        f"[yellow]No document found with source: {source}[/yellow]"
                    )
                    return False

        except psycopg2.Error as e:
            console.print(f"[red]Failed to delete document: {e}[/red]")
            self._connection.rollback()
            return False


def display_documents_table(documents: List[Dict[str, Any]]):
    """Display documents in a formatted table."""
    if not documents:
        console.print("[yellow]No documents found.[/yellow]")
        return

    table = Table(title="Vectorized Documents")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Source", style="green")
    table.add_column("Chunks", style="blue", justify="right")
    table.add_column("Created", style="yellow")

    for doc in documents:
        table.add_row(
            str(doc["id"]),
            doc["title"][:50] + "..." if len(doc["title"]) > 50 else doc["title"],
            doc["source"],
            str(doc["chunk_count"]),
            doc["created_at"].strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)
