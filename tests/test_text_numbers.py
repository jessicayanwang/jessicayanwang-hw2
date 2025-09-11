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
    # These should pass with your current text_to_number implementation
    for word, expected in [("zero", "0"), ("one", "1"), ("ten", "10"), ("nil", "0")]:
        got, err = call_convert(client, word, "text", "decimal")
        assert err is None
        assert got == expected

def test_text_multiword_example_from_readme(client):
    """README example: 'forty two' -> 42.
    This WILL FAIL on the current text_to_number (bug), because it only knows 0..10.
    Fix suggestion: use `text2digits` or a proper parser to support multiword numbers."""
    got, err = call_convert(client, "forty two", "text", "decimal")
    assert err is None, f"Converting text should not error. Got: {err}"
    assert got == "42"