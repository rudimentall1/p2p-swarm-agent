import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from node import load_or_generate_keys, sign_message, verify_signature

def test_keys():
    priv, pub = load_or_generate_keys("test_agent")
    assert priv is not None
    assert pub is not None

def test_signature():
    priv, pub = load_or_generate_keys("test_agent")
    msg = "test message"
    sig = sign_message(priv, msg)
    assert verify_signature(pub, msg, sig) is True
    assert verify_signature(pub, "wrong", sig) is False
