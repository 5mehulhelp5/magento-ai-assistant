#!/usr/bin/env python3
import typer
import subprocess

app = typer.Typer(help="Magento AI Assistant - Command Line Tool")

@app.command()
def magento_pull():
    """Fetch all Magento products (full pull)."""
    subprocess.run(["python", "-m", "src.ingestion.magento_full_pull"])

@app.command()
def magento_test():
    """Test Magento API connection and print sample products."""
    subprocess.run(["python", "-m", "src.ingestion.magento_test"])

@app.command()
def pdf_extract():
    """Extract sample text from PDF manual."""
    subprocess.run(["python", "-m", "src.ingestion.PDF.pdf_reader"])

@app.command()
def runserver(port: int = 8000):
    """Run FastAPI app."""
    subprocess.run(["uvicorn", "src.main:app", "--reload", "--port", str(port)])

@app.command()
def sync():
    """Run product sync script."""
    subprocess.run(["python", "-m", "src.ingestion.magento_sync"])

@app.command()
def data_preprocess():
    """Clean and standardize Magento + PDF product data."""
    subprocess.run(["python", "-m", "src.ingestion.preprocessor"])

@app.command()
def data_save():
    """Save cleaned data to JSON and CSV formats."""
    subprocess.run(["python", "-m", "src.ingestion.save_processor"])

# sync_parser = subparsers.add_parser('sync-delta', help='Run delta sync for updated products')
# sync_parser.add_argument('--page-size', type=int, default=100, help='API page size')
# sync_parser.set_defaults(func=cmd_sync_delta)
@app.command()
def sync_delta(page_size: int = 100):
    """Run delta sync for updated products."""
    subprocess.run(["python", "-m", "src.ingestion.sync_manager", "--page-size", str(page_size)])

@app.command("embed-products")
def embed_products():
    """Generate embeddings for all processed products."""
    from src.embeddings.embedder import ProductEmbedder
    embedder = ProductEmbedder()
    embedder.generate_embeddings()

if __name__ == "__main__":
    app()
