import os
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
from streamlit_feedback import streamlit_feedback
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
import base64
import uuid


def check_user_login() -> None:
    """
    Check whether the user is currently logged in the app.
    """

    if "authentication_status" not in st.session_state:
        switch_page("login")
    
    elif st.session_state["authentication_status"] == None:
        switch_page("login")


def clear_session_state() -> None:
    """
    Clear all items from session state for a new chat,
    except for authentication info.
    """

    for key in st.session_state:
        if key not in ["name", "username", "authentication_status"]:
            del(st.session_state[key])
    st.rerun()


def display_session_history() -> None:
    """
    Display user and AI messages in a given session.
    """

    for n, message in enumerate(st.session_state["messages"]):
        st.chat_message(message["role"]).markdown(message["response"])

        if (message["role"] == "assistant") and (n >= 1):
            
            exec_id = message["execution_id"]
            feedback_key = f"feedback_{exec_id}"
            
            try:
                score = st.session_state["execution_ids"][exec_id]["feedback"]["score"]
                streamlit_feedback(
                    feedback_type="thumbs",
                    disable_with_score=score,
                    key=feedback_key,
                )

            except:
                feedback = streamlit_feedback(
                    feedback_type="thumbs",
                    optional_text_label="Faça aqui os comentários que desejar",
                    key=feedback_key,
                )

                if feedback:
                    st.session_state["execution_ids"][exec_id].update({
                        "feedback": feedback
                    })


def hide_navigation_sidebar() -> None:
    """
    Hides the navigation generated automatically by Streamlit
    of all the pages located in 'pages' folder.
    """

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)


def initiate_session_state(filters: dict) -> None:
    """
    Start all items required in session state.

    Parameters
    ----------
    filters : dict
        Filters selected by the user.
    """

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    if "filters" not in st.session_state:
        st.session_state["filters"] = {}
    st.session_state["filters"].update(filters)

    if "execution_ids" not in st.session_state:
        st.session_state["execution_ids"] = {}


def load_users() -> stauth.Authenticate:
    """
    Load the users from the yaml file and configure
    authenticator for the app.
    
    Returns
    -------
    stauth.Authenticate
        Authenticator with users info.
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

    return authenticator


def page_config(layout: str = "centered", sidebar: str = "auto") -> None:
    """
    Set the page configuration for each page of the app.
    Must be the first command in each page, and it must be called
    only once.

    Parameters
    ----------
    layout : str
        Type of the layout of the page, by default 'centered'.
    sidebar : str
        Initial state of the sidebar, by default 'auto'.
    """

    icon_file_path = os.getenv("ICON_FILE_PATH")

    st.set_page_config(
        page_title="Chatbot de Notícias Poços",
        page_icon=f"{icon_file_path}/news.png",
        layout=layout,
        initial_sidebar_state=sidebar
    )
    hide_navigation_sidebar()


def sidebar() -> dict:
    """
    Generate the sidebar for the chat and get the filters.
    
    Returns
    -------
    dict
        Filters selected by the user.
    """

    sbar = st.sidebar

    sbar.subheader("")
    col_left, col_logo, col_right = sbar.columns([1, 2, 1])
    col_logo.image(f"{os.getenv('ICON_FILE_PATH')}/web-search.png")

    sbar.subheader("")

    user_exp = sbar.expander(f"Olá, _{st.session_state['name']}_")
    if user_exp.button("Alterar senha"):
        switch_page("reset_password")

    sbar.subheader("")

    col_left, col_button, col_right = sbar.columns([1.3, 2, 1])
    if col_button.button("Novo Chat"):
        clear_session_state()
    
    sbar.subheader("")

    expander = sbar.expander("Filtros", expanded=True)

    expander.write("")
    categories_list = ["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5"]
    categories = expander.multiselect("Categorias", options=categories_list, placeholder="Escolha uma opção")

    date_min = datetime.strptime("2021-01-01", "%Y-%m-%d")
    date_max = datetime.strptime("2023-09-30", "%Y-%m-%d")

    expander.divider()

    expander.write("")
    col_date_1, col_mid, col_date_2 = expander.columns([1, 0.1, 1])
    date_start = col_date_1.date_input("Data de início", value=date_min, min_value=date_min, max_value=date_max, format="DD/MM/YYYY")
    date_end = col_date_2.date_input("Data final", value=date_max, min_value=date_min, max_value=date_max, format="DD/MM/YYYY")

    filters = {
        "categories": categories,
        "date_start": date_start.strftime("%Y-%m-%d"),
        "date_end": date_end.strftime("%Y-%m-%d")
    }

    return filters


def set_background(file_name: str):
    """
    A function to unpack an image and set as background.
 
    Returns
    -------
    The background.
    """

    file_ext = "png"
    file_path = f"{os.environ['ICON_FILE_PATH']}/{file_name}.png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{file_ext};base64,{base64.b64encode(open(file_path, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
