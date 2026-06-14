import streamlit as st

from PIL import Image

import pytesseract  # type: ignore

from services.ai_service import summarize_text

st.title("🖼️ Image Summarizer")

image_file = st.file_uploader(
    "Upload Image",
    type=["png", "jpg", "jpeg"]
)

if image_file:
    image = Image.open(image_file)
    st.image(image)

    if st.button("Summarize Image"):
        with st.spinner("Extracting text and summarizing..."):
            try:
                extracted_text = pytesseract.image_to_string(image)
            except Exception as exc:
                st.error(f"Could not read the image. {exc}")
                extracted_text = ""

        if not extracted_text.strip():
            st.warning("No readable text was detected in the image.")
        else:
            summary = summarize_text(extracted_text)

            st.subheader("Summary")
            st.write(summary)
            