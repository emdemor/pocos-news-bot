import os, sys
from time import sleep

import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
from streamlit_extras.switch_page_button import switch_page

import ui
from ui.components import page_config, set_background, hide_navigation_sidebar


def front():
    
    st.set_page_config(
        page_title="Bot News",
        initial_sidebar_state="collapsed",
    )

    hide_navigation_sidebar()

    set_background("background-loading-page")

    sleep(1)

    switch_page("login")

def run():
    path = os.path.join(
        "/".join(os.path.abspath(ui.__file__).split("/")[:-1]),
        "__init__.py",
    )


    if runtime.exists():
        front()
    
    else:
        print(path)
        sys.argv = ["streamlit", "run", path]
        sys.exit(stcli.main())

if __name__ == "__main__":
    run()