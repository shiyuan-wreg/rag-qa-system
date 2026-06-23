"""Simple session-based authentication for DocHub."""

from itsdangerous import BadSignature, TimestampSigner


class AuthManager:
    def __init__(self, password: str, secret_key: str = "dochub-secret-key-change-in-production"):
        self._password = password
        self._signer = TimestampSigner(secret_key)

    def verify(self, password: str) -> bool:
        if not self._password:
            return True
        return password == self._password

    def create_session(self) -> str:
        return self._signer.sign("dochub-session").decode("utf-8")

    def verify_session(self, token: str) -> bool:
        if not self._password:
            return True
        if not token:
            return False
        try:
            self._signer.unsign(token, max_age=86400)
            return True
        except BadSignature:
            return False
