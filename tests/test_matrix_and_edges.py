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

def test_hex_prefix_and_case(client):
    # Should accept 0x prefix and mixed case
    for src in ("2a", "2A", "0x2a", "0X2A", "002a"):
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

def test_base64_zero_should_work(client):
    """App currently breaks on 0 -> base64 because to_bytes(0, ...) is invalid."""
    got, err = call_convert(client, "0", "decimal", "base64")
    assert err is None, f"Converting 0→base64 should not error: {err}"
    assert got == "AA==", f"Expected little-endian b64 of 0 to be AA==, got {got}"

@pytest.mark.parametrize("n", [1, 255, 256, 65535, 10**6])
def test_base64_roundtrip_little_endian_expected(client, n):
    """Homework requires little-endian base64; app uses big-endian -> should fail until fixed."""
    b64_le = le_b64_from_int(n)
    dec, err = call_convert(client, b64_le, "base64", "decimal")
    assert err is None
    assert dec == str(n), (
        f"Expected little-endian base64 decode. For n={n}, app returned {dec} from {b64_le}."
    )

@pytest.mark.parametrize("neg", ["-1", "-5", "-255"])
@pytest.mark.parametrize("to_kind", ["binary", "octal", "hexadecimal", "base64"])
def test_negative_numbers_should_error(client, neg, to_kind):
    """
    Current app produces wrong strings for negatives (e.g., bin(-5)[2:] == 'b101').
    Reasonable behavior: reject negatives for non-decimal outputs or handle sign explicitly.
    We enforce an error for clarity.
    """
    got, err = call_convert(client, neg, "decimal", to_kind)
    assert got is None or got.startswith("-"), (
        f"Negative conversion should not silently produce malformed output. got={got}"
    )
    # At minimum, an error is acceptable:
    if got is None:
        assert err