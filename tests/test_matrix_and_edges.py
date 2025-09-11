import itertools
import pytest
from .test_oracle_helpers import render, parse, le_b64_from_int

KINDS = ["binary", "octal", "decimal", "hexadecimal", "base64"]

def call_convert(client, input_value, input_type, output_type):
    resp = client.post(
        "/convert",
        json={"input": input_value, "inputType": input_type, "outputType": output_type},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    return data["result"], data["error"]

@pytest.mark.parametrize("n", [0, 1, 2, 7, 8, 15, 16, 31, 32, 63, 64, 255, 256, 1024, 65535, 10**6])
@pytest.mark.parametrize("from_kind,to_kind", list(itertools.product(KINDS, KINDS)))
def test_full_matrix_numeric(client, n, from_kind, to_kind):
    """Cross-validate all conversions using a stdlib oracle, including base64 (little-endian)."""
    src = render(n, from_kind)
    expected = render(parse(src, from_kind), to_kind)
    got, err = call_convert(client, src, from_kind, to_kind)
    assert err is None, f"Unexpected error for {from_kind}→{to_kind} with {src}: {err}"
    assert got == expected, f"{from_kind}→{to_kind} failed for {src}. expected={expected} got={got}"

def test_leading_zeros_binary(client):
    got, err = call_convert(client, "0001010", "binary", "decimal")
    assert err is None
    assert got == "10"

def test_hex_case_insensitive(client):
    for src in ("2a", "2A", "002a"):
        got, err = call_convert(client, src, "hexadecimal", "decimal")
        assert err is None
        assert got == "42"

def test_invalid_input_type(client):
    got, err = call_convert(client, "42", "frobnicate", "decimal")
    assert got is None
    assert "Invalid input type" in err

def test_invalid_number_string(client):
    got, err = call_convert(client, "not-a-number", "decimal", "binary")
    assert got is None
    assert err  # some error message

@pytest.mark.parametrize("n", [1, 255, 256, 65535, 10**6])
def test_base64_roundtrip_little_endian_expected(client, n):
    """This asserts the homework's required little-endian rule for base64.
    The current code uses big-endian, so this test should FAIL until you fix it."""
    b64_le = le_b64_from_int(n)              # oracle little-endian b64 for n
    # app: base64 -> decimal
    dec, err = call_convert(client, b64_le, "base64", "decimal")
    assert err is None
    assert dec == str(n), (
        f"Expected little-endian base64 decode. For n={n}, app returned {dec} from {b64_le}."
        " (Your code likely uses big-endian.)"
    )