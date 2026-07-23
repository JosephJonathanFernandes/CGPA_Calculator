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
