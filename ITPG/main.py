import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
import tempfile
import cloudinary
import cloudinary.uploader
import uuid

# Cloudinary setup
cloudinary.config(
    cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
    api_key=st.secrets["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["CLOUDINARY_API_SECRET"]
)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.title("🧾 Universal Product Extractor for Shopify")

uploaded_files = st.file_uploader("Upload product images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

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

    # Extract basic fields
    title = lines[0] if lines else "Untitled Product"
    handle = re.sub(r'\W+', '-', title.lower()).strip("-") + f"-{unique_suffix}"
    tags = ", ".join(set(lines))
    description = "<br>".join(lines)
    image_url = upload_image_to_cloudinary(image)

    return {
        "Handle": handle,
        "Title": title,
        "Body (HTML)": f"<p>{description}</p>",
        "Vendor": "Your Brand",
        "Product Category": "",
        "Product Type": "",
        "Tags": tags,
        "Published": "TRUE",
        "Option1 Name": "Title",
        "Option1 Value": title,
        "Variant SKU": f"SKU-{handle[:12]}",
        "Variant Grams": "",
        "Variant Inventory Tracker": "",
        "Variant Inventory Qty": 10,
        "Variant Inventory Policy": "continue",
        "Variant Fulfillment Service": "manual",
        "Variant Price": "999",  # Default editable price
        "Variant Compare At Price": "",
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Variant Barcode": "",
        "Image Src": image_url,
        "Image Position": "1",
        "Image Alt Text": title,
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
    for file in uploaded_files:
        image = Image.open(file)
        product_data = process_image(image, unique_suffix=str(uuid.uuid4())[:8])
        products.append(product_data)

    df = pd.DataFrame(products)

    st.subheader("📦 Shopify-Ready CSV Preview")
    st.dataframe(df)

    csv_data = df.to_csv(index=False)
    st.download_button("📥 Download Shopify CSV", data=csv_data, file_name="shopify_products.csv", mime="text/csv")
