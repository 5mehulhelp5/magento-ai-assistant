import re
from html import unescape
from typing import Dict, Any, Optional, List

def clean_text(text: str) -> str:
    """Clean HTML, extra spaces, and special entities from text."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)  # remove HTML tags
    text = re.sub(r"\s+", " ", text)      # normalize whitespace
    return text.strip()

def normalize_dimensions(text: str, sku: str = "", name: str = "") -> Optional[Dict[str, Any]]:
    """Enhanced: Extract dimensions from text, name, or SKU (e.g., '-0040' → 400mm length)."""
    if not text and not sku and not name:
        return None
    # Text patterns: "38mm slide thickness", "75% extension"
    dim_pattern = r'(\d+(?:\.\d+)?)\s*(mm|cm|in|inch)(?:\s+thickness|extension|length)?'
    matches = re.findall(dim_pattern, (text or ""), re.IGNORECASE)
    if matches:
        dims = {"length_mm": [], "thickness_mm": [], "extension_percent": []}
        for val, unit in matches:
            val = float(val)
            if unit in ['mm', 'cm']:
                dims["length_mm"].append(val if unit == 'mm' else val * 10)
            elif 'extension' in text.lower():
                dims["extension_percent"].append(val)
            else:
                dims["thickness_mm"].append(val)
        return dims if any(dims.values()) else None
    
    # Fallback: Parse from SKU/name (e.g., "DA4120-0040" → length 400mm)
    length_match = re.search(r'-(\d{3,4})(?:\D|$)', sku or name)
    if length_match:
        length_mm = int(length_match.group(1))
        return {"length_mm": [length_mm]}
    return None

def normalize_capacity(text: str) -> Optional[Dict[str, Any]]:
    """Enhanced: Extract load rating with ranges and units."""
    if not text:
        return None
    # Patterns: "upto 438-550kg", "up to 300kg", "45 kg"
    pattern = r'(?:load rating|capacity)\s*(?:upto|up to|of upto)?\s*(\d+(?:-\d+)?)\s*(kg|lbs|kg/lbs)?'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        value_str = match.group(1)
        unit = match.group(2).lower() if match.group(2) else "kg"
        if '-' in value_str:
            min_val, max_val = map(float, value_str.split('-'))
            return {"min": min_val, "max": max_val, "unit": unit}
        else:
            return {"value": float(value_str), "unit": unit}
    return None


def propagate_parent_attrs(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """Merge parent extractions into child (e.g., capacity from parent description)."""
    child_merged = child.copy()
    for key in ['description', 'features']:
        if not child_merged.get(key) and parent.get(key):
            child_merged[key] = parent[key]  # Propagate for extraction
    # Directly inherit non-overridable fields
    for key in ['capacity', 'dimensions', 'material', 'corrosion_resistant', 'uom', 'country_of_manufacture']:
        if child_merged.get(key) is None and parent.get(key) is not None:
            child_merged[key] = parent[key]
    return child_merged

def flatten_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Expand configurables/bundles into flat list, propagating parents."""
    flattened = []
    for prod in products:
        # Parent record
        flattened.append(prod)
        
        # Children/variants
        children = prod.get("children", []) or prod.get("bundle_items", [])
        parent_key = prod.get("sku")
        for child in children:
            if isinstance(child, dict):
                child_merged = propagate_parent_attrs(prod, child)
                child_merged["parent_sku"] = parent_key
                child_merged["is_variant"] = True
                flattened.append(child_merged)
    return flattened
