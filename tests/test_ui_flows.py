import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock
import sys

# Mock streamlit_local_storage to prevent custom component hang
mock_ls = MagicMock()
sys.modules['streamlit_local_storage'] = mock_ls

def test_app_loads_successfully():
    at = AppTest.from_file('main.py').run()
    assert not at.exception

def test_cgpa_inputs_with_none_state():
    """Verify render_inputs handles None in initial_state and session_state without crashing."""
    code = """
import streamlit as st
from src.layout import render_inputs

# Simulate user clearing a number input
st.session_state["sgpa_0"] = None
st.session_state["cgpa_num_courses"] = 8
st.session_state["cgpa_completed_semesters"] = 3

# Simulate initial state containing None (e.g. from backlog or reload)
render_inputs({"grades": [None, 8.5, None], "credits": [20, 20, 20]})
"""
    at = AppTest.from_string(code).run()
    assert not at.exception
    assert len(at.exception) == 0

