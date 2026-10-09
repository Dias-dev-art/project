import hashlib
import hmac

from app.core.security import verify_github_signature


def test_valid_signature():
    body = b"{}"
    sig = "sha256=" + hmac.new(b"s", body, hashlib.sha256).hexdigest()
    assert verify_github_signature("s", body, sig)


def test_invalid_signature():
    assert not verify_github_signature("s", b"{}", "sha256=bad")
