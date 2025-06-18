import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import io
import re
import tempfile
import cloudinary
import cloudinary.uploader
import uuid

# Streamlit app title
st.title("🧾 Bulk Clothing Product Extractor for Shopify (Cloud OCR Edition)")

# Cloudinary configuration using Streamlit Secrets
cloudinary.config(
    cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"]
)

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.title("🧾 Bulk Clothing Product Extractor for Shopify")

uploaded_files = st.file_uploader("Upload product images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def format_collection_name(name):
    return name.lower().capitalize()

def upload_image_to_cloudinary(pil_img):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        pil_img.save(tmp.name)
        try:
            result = cloudinary.uploader.upload(tmp.name)
            return result.get("secure_url", "")
        except Exception as e:
            st.error(f"Cloudinary Upload Failed: {e}")
            return ""

def process_image(image, unique_suffix):
    text = pytesseract.image_to_string(image)
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
            continue

        if any(word in lower for word in ["shirt", "dupatta", "trouser"]):
            piece_count += 1
            product_details.append(f"• {line}")
        elif in_care_section:
            care_instructions.append(f"• {line}")

    if not collection_name:
        collection_name = "Uncategorized"

    title_prefix = f"{piece_count}-Piece Digital Printed Lawn Suit" if piece_count else "Digital Printed Lawn Suit"
    full_title = f"{title_prefix} – {collection_name}"
    base_handle = re.sub(r'\W+', '-', full_title.lower()).strip("-")
    handle = f"{base_handle}-{unique_suffix}"

    image_url = upload_image_to_cloudinary(image)

    description = ""
    if product_details:
        description += "<strong>Product Details:</strong><br>" + "<br>".join(product_details) + "<br><br>"
    if care_instructions:
        description += "<strong>Care Instructions:</strong><br>" + "<br>".join(care_instructions)

    if not price:
        price = "4999"  # fallback price

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
        "Variant SKU": f"SKU-{handle[:12]}",
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
        "Image Src": image_url,
        "Image Position": "1",
        "Image Alt Text": full_title,
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
        "Variant Image": image_url,
        "Variant Weight Unit": "kg",
        "Variant Tax Code": "",
        "Cost per item": "",
        "Status": "active"
    }

if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded successfully!")

    products = []
    for i, file in enumerate(uploaded_files):
        image = Image.open(file)
        product_data = process_image(image, unique_suffix=str(uuid.uuid4())[:8])
        products.append(product_data)

    df = pd.DataFrame(products)

    st.subheader("📦 Shopify-Ready CSV Preview")
    st.dataframe(df)

    csv_data = df.to_csv(index=False)
    st.download_button("📥 Download Shopify CSV", data=csv_data, file_name="shopify_products.csv", mime="text/csv")
