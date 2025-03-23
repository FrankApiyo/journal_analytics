import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class LiveViewAuth(TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        """Validate the JWT with the external API."""
        response = requests.get(
            f"{settings.JOURNAL_API_URL}/api/auth_check",
            headers={"Authorization": f"Bearer {key}"},
        )

        if response.status_code != 200:
            raise AuthenticationFailed("Invalid token")

        return (None, key)  # No user object since we're not storing users
