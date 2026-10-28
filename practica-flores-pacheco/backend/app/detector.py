from urllib.parse import urlparse
import math
import re

SUSPICIOUS_TERMS = {"verify", "login", "secure", "urgent", "update", "account", "password", "bank", "confirm"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly"}

def analyze(value: str) -> tuple[float, str, list[str]]:
    text = value.strip()
    lower = text.lower()
    score = 0.0
    reasons: list[str] = []
    urls = re.findall(r"https?://[^\s<>'\"]+", text)
    if urls:
        for raw in urls:
            parsed = urlparse(raw)
            host = (parsed.hostname or "").lower()
            if parsed.scheme != "https":
                score += 20; reasons.append("URL sin HTTPS")
            if host in SHORTENERS:
                score += 20; reasons.append("Acortador de URL detectado")
            if host and (host.count("-") >= 2 or len(host) > 35):
                score += 15; reasons.append("Dominio con estructura anómala")
            if any(ord(c) > 127 for c in host):
                score += 25; reasons.append("Posible homograph attack")
            labels = host.split(".")
            if len(labels) > 3:
                score += 10; reasons.append("Exceso de subdominios")
            entropy = _entropy(host)
            if entropy > 3.8:
                score += 10; reasons.append("Entropía elevada en el dominio")
    term_hits = sorted({term for term in SUSPICIOUS_TERMS if term in lower})
    if term_hits:
        score += min(35, len(term_hits) * 7)
        reasons.append("Lenguaje de urgencia o solicitud de credenciales: " + ", ".join(term_hits))
    if "@" in text and urls:
        score += 10; reasons.append("URL potencialmente ofuscada en el contenido")
    score = min(100.0, round(score, 2))
    verdict = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
    if not reasons:
        reasons.append("No se identificaron señales heurísticas críticas")
    return score, verdict, reasons

def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())
