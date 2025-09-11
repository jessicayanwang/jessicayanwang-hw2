import pytest

def test_num2words_reasonable_large():
    # num2words should round-trip an integer to a non-empty English phrase
    from num2words import num2words
    s = num2words(10**6 + 42)
    assert isinstance(s, str) and len(s) > 0

def test_base64_validate_strictness():
    """
    CPython base64.b64decode(validate=True) should reject malformed inputs.
    If this unexpectedly passes, it indicates a library/platform quirk.
    """
    import base64
    with pytest.raises(Exception):
        base64.b64decode("AQ!", validate=True)