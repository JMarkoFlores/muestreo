from app.detector import analyze

def test_insecure_url_is_high_risk():
    score, verdict, reasons = analyze("http://secure-login-banco.example/verify")
    assert score >= 25
    assert verdict in {"medium", "high", "critical"}
    assert any("HTTPS" in reason for reason in reasons)

def test_clean_text_has_reason():
    score, verdict, reasons = analyze("Mensaje informativo sin enlaces")
    assert 0 <= score <= 100
    assert verdict == "low"
    assert reasons
