import os, sys
import streamlit as st
import uuid

from bot import NewsBot
from loguru import logger

sys.path.append(os.getcwd())
from ui.components import (
    check_user_login,
    display_session_history,
    initiate_session_state,
    page_config,
    sidebar,
)


def chat():
    st.title("Chatbot de Notícias - Poços de Caldas")

    display_session_history()

    if prompt := st.chat_input("Digite aqui..."):
        st.session_state["messages"].append({"role": "user", "response": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("..."):
            news_bot = load_news_bot()
            response = news_bot.execute(prompt)

        with st.chat_message("assistant"):
            st.markdown(response["response"])
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "response": response["response"],
                "execution_id": response["execution_id"],
            }
        )
        st.session_state["execution_ids"].update(
            {
                response["execution_id"]: {
                    "message": prompt,
                    "response": response["response"],
                    "filters": filters,
                }
            }
        )

        st.rerun()


@st.cache_resource(show_spinner=False)
def load_news_bot():
    return NewsBot(
        local_filepath=f"{st.session_state['username']}_{st.session_state['session_id']}.json"
    )


if __name__ == "__main__":
    page_config()
    check_user_login()
    filters = sidebar()
    initiate_session_state(filters)
    chat()
