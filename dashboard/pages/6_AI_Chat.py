import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from rag.chat_engine import answer_question

st.set_page_config(page_title="AI Research Chat", layout="wide")
st.title("🤖 AI Research Assistant")
st.caption(
    "Ask about recent news, sectors, or companies. This answers from your own "
    "indexed research data — it explains context, it never recommends buying or selling."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(message)

question = st.chat_input("e.g. What happened today in banking?")

if question:
    st.session_state.chat_history.append(("user", question))
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your research index..."):
            try:
                result = answer_question(question)
                st.write(result["answer"])
                if result["sources"]:
                    with st.expander("Sources"):
                        for s in result["sources"]:
                            st.write(f"- {s['source']}: {s['url']}")
                st.session_state.chat_history.append(("assistant", result["answer"]))
            except Exception as exc:
                error_msg = (
                    f"Couldn't get an answer: {exc}\n\n"
                    "Check that your LLM_PROVIDER and API key are set in `.env`."
                )
                st.error(error_msg)
                st.session_state.chat_history.append(("assistant", error_msg))
