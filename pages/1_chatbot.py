import streamlit as st
from services.ai_service import ask_ai

st.title("💬 AI Chatbot")

if "answer" not in st.session_state:
    st.session_state.answer = ""

question = st.text_area(
    "Ask Anything",
    key="chat_question"
)

if st.button("Send"):

    if question.strip():

        with st.spinner("Thinking..."):

            try:
                answer = ask_ai(question)
                st.session_state.answer = answer

            except Exception as e:
                st.session_state.answer = f"Error: {str(e)}"

    else:
        st.warning("Please enter a question.")

if st.session_state.answer:
    st.markdown("### Response")
    st.write(st.session_state.answer)