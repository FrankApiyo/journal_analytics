import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class LiveViewAuth(TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        """Validate the JWT with the external API and extract the user ID."""
        response = requests.get(
            f"{settings.JOURNAL_API_URL}/api/auth_check",
            headers={"Authorization": f"Bearer {key}"},
        )

        if response.status_code != 200:
            raise AuthenticationFailed("Invalid token")

        # Parse the response JSON
        try:
            data = response.json()
            user_id = data.get("user_id")
            if not user_id:
                raise AuthenticationFailed("User ID not found in token")
        except ValueError:
            raise AuthenticationFailed("Invalid token response")

        # Return a tuple of (None, token_payload)
        # Here, token_payload is a dictionary containing the key and user_id
        return (None, {"key": key, "user_id": user_id})
