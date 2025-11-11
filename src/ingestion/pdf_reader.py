import fitz  # PyMuPDF
import re
import os
import json

# ---------- CONFIG ----------
PDF_FOLDER = "data/samples"
RAW_OUTPUT_FOLDER = "data/processed/raw"
STRUCTURED_OUTPUT_FILE = "data/processed/product_specs.json"

# ---------- HELPER FUNCTIONS ----------
def extract_text_from_pdf(pdf_path):
    """Extract full text from a PDF."""
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return None
    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_specs(text):
    """Extract structured specs from text using regex."""
    specs = {}
    
    match = re.search(r"Dimensions[:\s]+([\d.x\s]+)", text, re.IGNORECASE)
    specs['dimensions'] = match.group(1).strip() if match else None
    
    match = re.search(r"Weight[:\s]+([\d.]+\s*kg)", text, re.IGNORECASE)
    specs['weight'] = match.group(1).strip() if match else None
    
    match = re.search(r"Power[:\s]+([\d.]+\s*W)", text, re.IGNORECASE)
    specs['power'] = match.group(1).strip() if match else None
    
    match = re.search(r"Material[:\s]+([\w\s]+)", text, re.IGNORECASE)
    specs['material'] = match.group(1).strip() if match else None
    
    return specs

# ---------- MAIN SCRIPT ----------
def process_all_pdfs(pdf_folder, raw_output_folder, structured_output_file):
    os.makedirs(raw_output_folder, exist_ok=True)
    os.makedirs(os.path.dirname(structured_output_file), exist_ok=True)
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_folder}")
        return
    
    all_specs = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"📄 Processing {pdf_file}...")
        
        # Infer SKU from filename, e.g., DS3031_manual.pdf → DS3031
        sku = pdf_file.split("_")[0]
        
        # --- Extract text ---
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue
        
        # Save raw text per SKU
        raw_output_file = os.path.join(raw_output_folder, f"{sku}_manual.json")
        with open(raw_output_file, "w", encoding="utf-8") as f:
            json.dump({"sku": sku, "manual_text": text}, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved raw text to {raw_output_file}")
        
        # --- Extract structured specs ---
        specs = extract_specs(text)
        specs['product_id'] = sku  # using SKU as product_id
        all_specs.append(specs)
    
    # Save all structured specs to a single JSON
    with open(structured_output_file, "w", encoding="utf-8") as f:
        json.dump(all_specs, f, indent=2, ensure_ascii=False)
    print(f"\n🎉 All structured specs saved to {structured_output_file}")

if __name__ == "__main__":
    process_all_pdfs(PDF_FOLDER, RAW_OUTPUT_FOLDER, STRUCTURED_OUTPUT_FILE)
