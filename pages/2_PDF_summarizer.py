import streamlit as st

from services.ai_service import extract_text_from_pdf, summarize_text

st.title("📄 PDF Summarizer")

pdf_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if pdf_file:
    st.info("Upload a PDF to generate a quick summary.")

    text = extract_text_from_pdf(pdf_file)

    st.write("DEBUG TEXT LENGTH:", len(text))
    st.write(text[:500])

    if not text.strip():
        st.warning("The PDF did not contain readable text. Try uploading a text-based PDF or a scanned PDF with OCR support.")

    if st.button("Generate Summary"):
        if not text.strip():
            st.warning("No readable text was found in the PDF.")
        else:
            with st.spinner("Summarizing PDF..."):
                summary = summarize_text(text)

            st.subheader("Summary")
            st.write(summary)
            