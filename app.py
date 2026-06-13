import streamlit as st

st.set_page_config(
    page_title="SmartAssist AI",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero {
        padding: 1.5rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        color: white;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
        margin-bottom: 1.25rem;
    }
    .hero h1 { margin-bottom: 0.3rem; }
    .card {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.8rem;
    }
    .feature-list { line-height: 1.7; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🤖 SmartAssist AI</h1>
        <p>Your polished AI assistant for chatting, planning, writing, translating, and summarizing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([2, 1])

with left:
    st.markdown(
        """
        <div class="card">
            <h3>What you can do</h3>
            <div class="feature-list">
                • 💬 Chat with the AI assistant<br>
                • 📄 Summarize PDFs and text<br>
                • 🌐 Translate content quickly<br>
                • 📧 Draft polished emails<br>
                • 📅 Plan tasks with reminders
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="card">
            <h3>Get started</h3>
            <p>Select a feature from the sidebar to begin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )