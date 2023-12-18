import sys, os
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

sys.path.append(os.getcwd())
from ui.src.components import load_users, page_config

page_config(sidebar="collapsed")


def login_users() -> None:
    """
    Load registered users and validade login attempt.
    """

    authenticator = load_users()
    authenticator.login("Login", "main")
    if st.button("Registrar"):
        switch_page("register")

    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'main', key='unique_key')
        switch_page("chat")

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')

    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    login_users()
