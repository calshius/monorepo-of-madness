"""Configuration management for RAG Magic."""

import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

console = Console()


class Config:
    """Configuration management for RAG Magic."""

    def __init__(self):
        """Initialize configuration from environment variables and .env files."""
        # Load .env files from current directory and project root
        self._load_env_files()

        # Database configuration
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.db_name = os.getenv("POSTGRES_DB", "rag_database")
        self.db_user = os.getenv("POSTGRES_USER", "rag_user")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "rag_password")

        # Google Gemini configuration
        self.gemini_api_key = os.getenv("GEMINI_TOKEN") or os.getenv("GOOGLE_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        self.chat_model = os.getenv("CHAT_MODEL", "gemini-1.5-flash")

        # Default settings
        self.default_chunk_size = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
        self.default_chunk_overlap = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))
        self.default_similarity_threshold = float(
            os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.7")
        )
        self.default_max_results = int(os.getenv("DEFAULT_MAX_RESULTS", "10"))

    def _load_env_files(self):
        """Load environment variables from .env files."""
        # Look for .env files in current directory and parent directories
        current_path = Path.cwd()

        # Check current directory and up to 3 parent directories
        for i in range(4):
            env_file = current_path / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                console.print(f"[green]✓ Loaded config from {env_file}[/green]")
                break
            current_path = current_path.parent

        # Also check postgres subdirectory if it exists
        postgres_env = Path("postgres/.env")
        if postgres_env.exists():
            load_dotenv(postgres_env)
            console.print(f"[green]✓ Loaded config from {postgres_env}[/green]")

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        errors = []

        if not self.gemini_api_key:
            errors.append("GEMINI_TOKEN or GOOGLE_API_KEY is required")

        if errors:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"[red]  • {error}[/red]")
            return False

        return True

    def display(self):
        """Display current configuration (masking sensitive data)."""
        console.print("[blue]Current Configuration:[/blue]")
        console.print(f"  Database Host: {self.db_host}")
        console.print(f"  Database Port: {self.db_port}")
        console.print(f"  Database Name: {self.db_name}")
        console.print(f"  Database User: {self.db_user}")
        console.print(f"  Database Password: {'*' * len(self.db_password)}")

        api_key_display = (
            f"{self.gemini_api_key[:8]}..."
            if self.gemini_api_key
            else "[red]Not set[/red]"
        )
        console.print(f"  Gemini API Key: {api_key_display}")
        console.print(f"  Embedding Model: {self.embedding_model}")
        console.print(f"  Chat Model: {self.chat_model}")
        console.print(f"  Default Chunk Size: {self.default_chunk_size}")
        console.print(f"  Default Chunk Overlap: {self.default_chunk_overlap}")
        console.print(
            f"  Default Similarity Threshold: {self.default_similarity_threshold}"
        )
        console.print(f"  Default Max Results: {self.default_max_results}")

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def create_sample_env_file(file_path: str = ".env"):
    """Create a sample .env file with all configuration options."""
    sample_content = """# RAG Magic Configuration

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_database
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

# Google Gemini Configuration (Required)
GEMINI_TOKEN=your_gemini_api_key_here
# Alternative: GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
EMBEDDING_MODEL=models/text-embedding-004
CHAT_MODEL=gemini-1.5-flash

# Default Settings
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
DEFAULT_SIMILARITY_THRESHOLD=0.7
DEFAULT_MAX_RESULTS=10
"""

    env_path = Path(file_path)
    if env_path.exists():
        console.print(f"[yellow]⚠ File {file_path} already exists[/yellow]")
        return False

    with open(env_path, "w") as f:
        f.write(sample_content)

    console.print(f"[green]✓ Created sample environment file: {file_path}[/green]")
    console.print("[yellow]Please edit the file and add your Gemini API key[/yellow]")
    return True
