import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/md_converter_app")

from auth import AuthManager


def test_verify_password():
    auth = AuthManager("secret")
    assert auth.verify("secret") is True
    assert auth.verify("wrong") is False


def test_session_roundtrip():
    auth = AuthManager("secret")
    token = auth.create_session()
    assert auth.verify_session(token) is True
    assert auth.verify_session("invalid") is False


def test_disabled_auth_when_no_password():
    auth = AuthManager("")
    assert auth.verify_session("") is True
