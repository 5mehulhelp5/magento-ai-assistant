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
    subprocess.run(["python", "-m", "src.ingestion.pdf_extract_sample"])

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

if __name__ == "__main__":
    app()
