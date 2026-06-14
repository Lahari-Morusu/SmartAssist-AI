import streamlit as st

from services.ai_service import ask_ai

st.title("📧 Email Writer")

purpose = st.text_input(
    "Purpose of Email",
    placeholder="What should the email be about?"
)

tone = st.selectbox(
    "Tone",
    ["Professional", "Formal", "Friendly"]
)

if st.button("Generate Email"):
    if not purpose.strip():
        st.warning("Please describe the purpose of the email.")
    else:
        with st.spinner("Writing your email..."):
            prompt = f"""
            Write a {tone} email that is clear, concise, and polished.

            Purpose:
            {purpose}
            """

            email = ask_ai(prompt)

        st.subheader("Generated Email")
        st.text_area(
            "Generated Email",
            email,
            height=300
        )
        