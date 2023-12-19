import os
import sys

import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

import ui

from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    ui.run()