from celery import shared_task
import requests
from .models import UserDocument


@shared_task
def sync_user_documents(token):
    """Fetch the latest user documents from the external API."""
    response = requests.get(
        "http://localhost:4000/api/user_documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    if response.status_code == 200:
        data = response.json().get("documents", [])

        for doc in data:
            UserDocument.objects.update_or_create(
                id=doc["id"], defaults={"name": doc["name"], "body": doc["body"]}
            )
