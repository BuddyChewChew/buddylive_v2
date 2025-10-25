# py/sanitize_epg.py
import re
import sys
from pathlib import Path

FILES = ["en/videoall.m3u", "en/videoall.xml"]

REPLACEMENTS = [
    # Bearer tokens
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-\._~+/=]+", re.IGNORECASE), r"\1[REDACTED]"),
    # common api keys / tokens in key:value or key=value patterns
    (re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token|token|secret|password)(\s*[:=]\s*)([^&\s\"']+)", re.IGNORECASE), r"\1\2[REDACTED]"),
    # AWS Access Key
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    # Private keys (multi-line)
    (re.compile(r"-----BEGIN (RSA|PRIVATE|OPENSSH) PRIVATE KEY-----(.*?)-----END (RSA|PRIVATE|OPENSSH) PRIVATE KEY-----", re.DOTALL), "[REDACTED_PRIVATE_KEY]"),
    # SSH public key long token
    (re.compile(r"ssh-(rsa|ed25519)\s+[A-Za-z0-9+/=]{100,}"), "[REDACTED_SSH_KEY]"),
    # Basic auth in URL user:pass@
    (re.compile(r"(https?:\/\/)[^\/\s:@]+:[^\/\s:@]+@"), r"\1[REDACTED_AUTH]@"),
]

suspicious_found = []

for file in FILES:
    p = Path(file)
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    original = text
    for pattern, repl in REPLACEMENTS:
        text, count = pattern.subn(repl, text)
        if count:
            suspicious_found.append((file, pattern.pattern, count))
    # Overwrite with sanitized content
    p.write_text(text, encoding="utf-8")

if suspicious_found:
    print("Sanitizer: redacted suspicious patterns:")
    for f, pat, cnt in suspicious_found:
        print(f" - {f}: {cnt} match(es) for pattern: {pat}")
else:
    print("Sanitizer: no suspicious patterns found.")

# exit 0 so workflow continues; to fail on detection, uncomment following:
# if suspicious_found: sys.exit(2)
