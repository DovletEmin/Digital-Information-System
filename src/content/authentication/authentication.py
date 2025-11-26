from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationNoBearerRequired(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except AuthenticationFailed:
            return None

    def get_raw_token(self, header):
        parts = header.strip().split()

        if len(parts) == 0:
            return None

        token = parts[-1]

        if isinstance(token, bytes):
            return token.decode("utf-8")
        return token
