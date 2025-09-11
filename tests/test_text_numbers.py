import pytest

def call_convert(client, input_value, input_type, output_type):
    resp = client.post(
        "/convert",
        json={"input": input_value, "inputType": input_type, "outputType": output_type},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    return data["result"], data["error"]

def test_text_basic_words_supported_today(client):
    # These should pass with current text_to_number implementation
    for word, expected in [("zero", "0"), ("one", "1"), ("ten", "10"), ("nil", "0")]:
        got, err = call_convert(client, word, "text", "decimal")
        assert err is None
        assert got == expected

def test_text_multiword_example_from_readme(client):
    """README example: 'forty two' -> 42.
    This WILL FAIL until text_to_number supports multiword numbers (bug in app.py)."""
    got, err = call_convert(client, "forty two", "text", "decimal")
    assert err is None, f"Converting text should not error. Got: {err}"
    assert got == "42"

@pytest.mark.parametrize("phrase,expected", [
    ("twenty-one", "21"),
    ("Two Hundred Three", "203"),
    ("one thousand and five", "1005"),
])
def test_text_reasonable_multiword_variants(client, phrase, expected):
    """
    Reasonable English number phrases should work or clearly error.
    We expect correct results (aligns with README intent).
    """
    got, err = call_convert(client, phrase, "text", "decimal")
    assert err is None
    assert got == expected