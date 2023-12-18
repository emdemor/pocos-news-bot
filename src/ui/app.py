import os, sys
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from time import sleep

from dotenv import load_dotenv

sys.path.append(os.getcwd())
from ui.src.components import page_config, set_background

load_dotenv()
page_config(sidebar="collapsed")

set_background("background-loading-page")

sleep(3)

switch_page("login")
