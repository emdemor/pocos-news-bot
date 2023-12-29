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

page_config()
check_user_login()



def chat(news_bot: NewsBot):
    
    filters = sidebar()
    initiate_session_state(filters)
    session = st.session_state["session_id"]

    st.title("Chatbot de Notícias - Poços de Caldas")

    display_session_history()

    if prompt := st.chat_input("Digite aqui..."):
        st.session_state["messages"].append({"role": "user", "response": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("..."):
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


if __name__ == "__main__":
    logger.info("Instance of chatbot")
    news_bot = NewsBot()
    logger.info("Starting chat")
    chat(news_bot)
