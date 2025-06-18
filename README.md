# 🧾 Shopify CSV Generator (Image-to-Product Extractor)

**Instantly generate Shopify-ready product CSV files by uploading product images.**

This Streamlit web app uses OCR (Tesseract) and Cloudinary to extract text from images and convert the data into a properly structured Shopify CSV. It’s designed to help you bulk-create product listings in just a few clicks.

---

## 🚀 Features

- 📸 **Upload Product Images**: Drag and drop multiple images (JPG, JPEG, PNG).
- 🔍 **OCR-Based Text Extraction**: Automatically pulls product data from images using Tesseract OCR.
- ☁️ **Cloudinary Integration**: Images are uploaded to Cloudinary and linked in the CSV.
- 🧠 **Smart Text Parsing**: Extracts and formats:
  - Product title
  - Price (PKR or other currency)
  - Product details
  - Care instructions
  - Tags, SKU, and more
- 📊 **Shopify CSV Format**: Outputs a full CSV file compatible with Shopify import.
- 💾 **Download CSV**: Instantly download your generated CSV.

---

## 🛠️ Requirements

- Python 3.9+
- Tesseract OCR installed and added to PATH
- Cloudinary account

---

## 📦 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/shopify-csv-generator.git
   cd shopify-csv-generator
