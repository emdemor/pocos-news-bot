import os, sys
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader
from time import sleep

sys.path.append(os.getcwd())
from ui.components import check_user_login, page_config

page_config(sidebar="collapsed")
check_user_login()


def reset_password() -> None:
    """
    Reset the password for a logged user.
    """

    with open(os.environ['USERS_STORAGE']) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], 'Alterar senha'):
                with open(os.environ['USERS_STORAGE'], 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('Senha modificada com sucesso.')
                with st.spinner("Aguarde..."):
                    sleep(3)
                switch_page("chat")
        except Exception as e:
            st.error(e)

if __name__ == "__main__":
    reset_password()
