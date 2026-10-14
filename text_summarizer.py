import streamlit as st
from llm import ask_ai

st.set_page_config(page_title="AI-Powered Text Summarizer")
st.title("AI-Powered Text Summarizer")

text = st.text_area("Enter a paragraph or article:", height=250)

if st.button("Summarize"):
    if not text.strip():
        st.warning("Please enter some text before clicking Summarize.")
    else:
        prompt = (
            "Summarize the following text in a short, clear summary "
            "(3-4 sentences):\n\n" + text
        )
        with st.spinner("Summarizing..."):
            summary = ask_ai(prompt)
        st.subheader("Summary")
        st.write(summary)