import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import io

# Tesseract path setup (you already have this right!)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.title("🧵 Clothing Product Text Extractor to CSV")

uploaded_file = st.file_uploader("Upload a product image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🧠 Extract & Generate CSV"):
        extracted_text = pytesseract.image_to_string(image)

        # Show extracted text
        st.subheader("📝 Extracted Text")
        st.text_area("Raw Text", value=extracted_text, height=300)

        # Clean & structure data
        lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
        if lines:
            title = lines[0]
            price = ''
            body_lines = []

            for line in lines[1:]:
                if 'PKR' in line.upper():
                    price = ''.join(filter(str.isdigit, line))
                else:
                    body_lines.append(line)

            body = '\n'.join(body_lines)

            # Create DataFrame
            df = pd.DataFrame([{
                "Title": title,
                "Body (HTML)": body,
                "Price": price,
                "Vendor": "YourBrand",
                "Tags": "",
            }])

            st.subheader("📦 CSV Preview")
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="product_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("❌ No text found in image.")
