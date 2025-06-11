import streamlit as st
from PIL import Image
import cloudinary
import cloudinary.uploader
import pandas as pd
import re
import tempfile

# Streamlit app title
st.title("🧾 Bulk Clothing Product Extractor for Shopify (Cloud OCR Edition)")

# Cloudinary configuration using Streamlit Secrets
cloudinary.config(
    cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"]
)

# File uploader
uploaded_files = st.file_uploader("Upload product images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Helper function to format collection name
def format_collection_name(name):
    return name.lower().capitalize()

# Function to extract text using Cloudinary OCR
def extract_text_from_image(image_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image_file.save(tmp.name)
        response = cloudinary.uploader.upload(tmp.name, ocr="adv_ocr")
        text_data = response.get("info", {}).get("ocr", {}).get("adv_ocr", {}).get("data", [])
        if text_data and "textAnnotations" in text_data[0]:
            return text_data[0]["textAnnotations"][0]["description"]
    return ""

# Image processing and CSV preparation
def process_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    price = ''
    collection_name = ''
    product_details = []
    care_instructions = []
    in_care_section = False
    piece_count = 0

    for line in lines:
        lower = line.lower()

        if "www.ibbonanza.com" in lower or "©" in line or "prinfed" in lower:
            continue

        if "pkr" in lower:
            match = re.search(r"(\d{3,6})", line)
            if match:
                price = match.group(1)
            continue

        if not collection_name and line.isupper() and len(line) < 25 and " " in line:
            collection_name = format_collection_name(line)
            continue

        if "care" in lower and "instruction" in lower:
            in_care_section = True
            continue

        if re.match(r'^[a-zA-Z]{1}-\d+', line):
            continue  # Skip product codes

        if any(word in lower for word in ["shirt", "dupatta", "trouser"]):
            piece_count += 1
            product_details.append(f"• {line}")
        elif in_care_section:
            care_instructions.append(f"• {line}")

    title_prefix = f"{piece_count}-Piece Digital Printed Lawn Suit" if piece_count else "Digital Printed Lawn Suit"
    full_title = f"{title_prefix} – {collection_name}" if collection_name else title_prefix
    handle = re.sub(r'\W+', '-', full_title.lower()).strip("-")

    description = ""
    if product_details:
        description += "<strong>Product Details:</strong><br>" + "<br>".join(product_details) + "<br><br>"
    if care_instructions:
        description += "<strong>Care Instructions:</strong><br>" + "<br>".join(care_instructions)

    return {
        "Handle": handle,
        "Title": full_title,
        "Body (HTML)": description,
        "Vendor": "Al Wahid Fashion",
        "Product Category": "Clothing > Outfit Sets",
        "Product Type": "Clothing",
        "Tags": f"Lawn,{piece_count}-Piece,{collection_name}",
        "Published": "TRUE",
        "Option1 Name": "Title",
        "Option1 Value": full_title,
        "Variant SKU": "",
        "Variant Grams": "",
        "Variant Inventory Tracker": "",
        "Variant Inventory Qty": 10,
        "Variant Inventory Policy": "continue",
        "Variant Fulfillment Service": "manual",
        "Variant Price": price,
        "Variant Compare At Price": "",
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Variant Barcode": "",
        "Image Src": "",
        "Image Position": "",
        "Image Alt Text": "",
        "Gift Card": "FALSE",
        "SEO Title": "",
        "SEO Description": "",
        "Google Shopping / Google Product Category": "",
        "Google Shopping / Gender": "",
        "Google Shopping / Age Group": "",
        "Google Shopping / MPN": "",
        "Google Shopping / AdWords Grouping": "",
        "Google Shopping / AdWords Labels": "",
        "Google Shopping / Condition": "",
        "Google Shopping / Custom Product": "",
        "Google Shopping / Custom Label 0": "",
        "Google Shopping / Custom Label 1": "",
        "Google Shopping / Custom Label 2": "",
        "Google Shopping / Custom Label 3": "",
        "Google Shopping / Custom Label 4": "",
        "Variant Image": "",
        "Variant Weight Unit": "kg",
        "Variant Tax Code": "",
        "Cost per item": "",
        "Status": "active"
    }

# Main Streamlit logic
if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded successfully!")

    products = []
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        text = extract_text_from_image(img)
        product = process_text(text)
        products.append(product)

    df = pd.DataFrame(products)

    st.subheader("📦 Shopify-Ready CSV Preview")
    st.dataframe(df)

    csv_data = df.to_csv(index=False)
    st.download_button("📥 Download Shopify CSV", data=csv_data, file_name="shopify_products.csv", mime="text/csv")
