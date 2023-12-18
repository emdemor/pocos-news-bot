import os, sys
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader
from time import sleep

sys.path.append(os.getcwd())
from ui.src.components import page_config

page_config(sidebar="collapsed")


def register_users() -> None:
    """
    Reset the password for a logged user.
    """

    with open('ui/users/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    try:
        if authenticator.register_user('Registrar usuário', preauthorization=False):
            with open('ui/users/config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('Usuário registrado com sucesso!')
            with st.spinner("Aguarde..."):
                sleep(3)
            switch_page("chat")
    except Exception as e:
        st.error(e)

if __name__ == "__main__":
    register_users()
