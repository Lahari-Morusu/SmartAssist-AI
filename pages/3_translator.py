import streamlit as st

from services.ai_service import translate_text

st.title("🌐 Translator")

text = st.text_area(
    "Enter Text",
    placeholder="Type the text you want translated..."
)

source = st.selectbox(
    "Source Language",
    ["English", "Telugu", "Hindi"]
)

target = st.selectbox(
    "Target Language",
    ["English", "Telugu", "Hindi"]
)

if st.button("Translate"):
    if not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        with st.spinner("Translating..."):
            prompt = f"""
            Translate the following text from {source} to {target}.
            Return only the translated text.

            Text:
            {text}
            """

            result = translate_text(prompt)

        st.subheader("Translated Text")
        st.success(result)