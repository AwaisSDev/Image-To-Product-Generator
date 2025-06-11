import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import io
import re

# Tesseract executable path (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.title("🧾 Bulk Clothing Product Extractor for Shopify")

uploaded_files = st.file_uploader("Upload product images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def format_collection_name(name):
    name = name.lower().capitalize()
    return name

def process_image(image):
    extracted_text = pytesseract.image_to_string(image)
    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
    cleaned_lines = []
    price = ''
    product_code = ''
    collection_name = ''
    found_fabrics = []

    for line in lines:
        lower = line.lower()

        # Skip supplier info or weird symbols
        if "www.ibbonanza.com" in lower or "©" in line or "prinfed" in lower:
            continue

        # Price extraction
        if "pkr" in lower:
            price_match = re.search(r"(\d{3,6})", line)
            if price_match:
                price = price_match.group(1)
            continue

        # Product code (e.g., V-541)
        if re.match(r"^[A-Z]-\d{3}", line):
            product_code = line
            continue

        # Fabric components
        if "shirt" in lower or "dupatta" in lower or "trouser" in lower:
            found_fabrics.append(line)

        # Collection name: early all-uppercase word, avoid © etc.
        if not collection_name and line.isupper() and len(line) <= 20 and not any(c in line for c in "©|/\\"):
            collection_name = format_collection_name(line)
            continue

        cleaned_lines.append(line)

    # Title generation
    piece_count = len(found_fabrics)
    title_prefix = f"{piece_count}-Piece Digital Printed Lawn Suit" if piece_count else "Lawn Suit"
    title = f"{title_prefix} – {collection_name}" if collection_name else title_prefix
    category = "Clothing"

    return {
        "Handle": re.sub(r'\s+', '-', title.lower()).replace("–", "").strip("-"),
        "Title": title,
        "Body (HTML)": "<br>".join(cleaned_lines),
        "Vendor": "Al Wahid Fashion",
        "Product Type": category,
        "Tags": f"Lawn,{piece_count}-Piece,{collection_name}",
        "Published": "TRUE",
        "Option1 Name": "Title",
        "Option1 Value": title,
        "Variant Price": price,
        "Variant Inventory Qty": 10,
        "Variant Inventory Policy": "deny",
        "Variant Fulfillment Service": "manual",
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
    }

if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded successfully!")

    results = []
    for file in uploaded_files:
        image = Image.open(file)
        result = process_image(image)
        results.append(result)

    df = pd.DataFrame(results)

    st.subheader("📦 Extracted Product Data")
    st.dataframe(df)

    # Download CSV button
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Shopify CSV", data=csv, file_name="shopify_products.csv", mime="text/csv")
