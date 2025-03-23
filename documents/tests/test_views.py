from unittest.mock import patch
from django.test.utils import override_settings
from rest_framework import status
from rest_framework import permissions
from rest_framework.test import APITestCase
from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from documents.views import UserDocumentViewSet


class TestAuth4(BaseAuthentication):
    """Mock authentication for tests."""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid token")

        key = auth_header.split("Bearer ")[1]

        return (None, {"key": key, "user_id": 4, "role": "default"})


class TestAuth2(BaseAuthentication):
    """Mock authentication for tests."""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid token")

        key = auth_header.split("Bearer ")[1]

        return (None, {"key": key, "user_id": 2, "role": "defualt"})


class TestAuth2Admin(BaseAuthentication):
    """Mock authentication for tests."""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid token")

        key = auth_header.split("Bearer ")[1]

        return (None, {"key": key, "user_id": 2, "role": "admin"})


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": ("documents.tests.test_views.TestAuth4",)
    }
)
class UserDocumentViewSetTest(APITestCase):
    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer test_token")

        self.doc1 = UserDocument.objects.create(
            id="e295ca17-c6de-4d44-b003-ffefefa7a805",
            user_id=4,
            name="Doc A",
            body="Content A",
        )
        self.doc2 = UserDocument.objects.create(
            id="95008107-98f8-4da4-b35c-f1b3fd2a5289",
            user_id=4,
            name="Doc B",
            body="Content B",
        )

    @patch("documents.tasks.sync_user_documents.delay")
    @patch.object(UserDocumentViewSet, "permission_classes", [permissions.AllowAny])
    @patch.object(UserDocumentViewSet, "authentication_classes", [TestAuth4])
    def test_list_documents_triggers_sync_task(self, mock_sync):
        """Test that listing documents triggers the async sync task."""
        response = self.client.get("/api/user_documents/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_sync.assert_called_once_with("test_token")

    @patch("documents.tasks.sync_user_documents.delay")
    @patch.object(UserDocumentViewSet, "permission_classes", [permissions.AllowAny])
    @patch.object(UserDocumentViewSet, "authentication_classes", [TestAuth4])
    def test_list_documents_returns_documents_user4(self, mock_sync):
        """Test that the view returns user documents without executing the sync task."""
        response = self.client.get("/api/user_documents/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = UserDocumentSerializer([self.doc1, self.doc2], many=True).data

        self.assertEqual(response.json(), expected_data)

        mock_sync.assert_called_once_with("test_token")

    @patch("documents.tasks.sync_user_documents.delay")
    @patch.object(UserDocumentViewSet, "permission_classes", [permissions.AllowAny])
    @patch.object(UserDocumentViewSet, "authentication_classes", [TestAuth2Admin])
    def test_list_documents_returns_documents_user4(self, mock_sync):
        """Test that the view returns user documents without executing the sync task."""
        response = self.client.get("/api/user_documents/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = UserDocumentSerializer([self.doc1, self.doc2], many=True).data

        self.assertEqual(response.json(), expected_data)

        mock_sync.assert_called_once_with("test_token")

    @patch("documents.tasks.sync_user_documents.delay")
    @patch.object(UserDocumentViewSet, "permission_classes", [permissions.AllowAny])
    @patch.object(UserDocumentViewSet, "authentication_classes", [TestAuth2])
    def test_list_documents_returns_documents_user2(self, mock_sync):
        """Test that the view returns user documents without executing the sync task."""
        response = self.client.get("/api/user_documents/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), [])

        mock_sync.assert_called_once_with("test_token")

    @patch.object(UserDocumentViewSet, "authentication_classes", [TestAuth4])
    def test_unauthenticated_user_cannot_access_documents(self):
        """Test that an unauthenticated user is denied access."""
        self.client.credentials()  # Remove authentication

        response = self.client.get("/api/user_documents/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
