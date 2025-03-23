from unittest.mock import patch
from django.test import TestCase
from documents.tasks import sync_user_documents
from documents.models import UserDocument


class SyncUserDocumentsTest(TestCase):
    @patch("documents.tasks.requests.get")  # Mock the API request
    def test_sync_user_documents_creates_new_docs(self, mock_get):
        """Test if the function creates new user documents with user_id."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "e295ca17-c6de-4d44-b003-ffefefa7a805",
                "user_id": 1,
                "name": "Doc A",
                "body": "Content A",
            },
            {
                "id": "95008107-98f8-4da4-b35c-f1b3fd2a5289",
                "user_id": 2,
                "name": "Doc B",
                "body": "Content B",
            },
        ]

        sync_user_documents("fake_token")

        # Check if documents were created with correct user_id
        self.assertEqual(UserDocument.objects.count(), 2)
        self.assertTrue(
            UserDocument.objects.filter(
                id="e295ca17-c6de-4d44-b003-ffefefa7a805", name="Doc A", user_id=1
            ).exists()
        )
        self.assertTrue(
            UserDocument.objects.filter(
                id="95008107-98f8-4da4-b35c-f1b3fd2a5289", name="Doc B", user_id=2
            ).exists()
        )

    @patch("documents.tasks.requests.get")
    def test_sync_user_documents_updates_existing_docs(self, mock_get):
        """Test if the function updates existing user documents with user_id."""
        UserDocument.objects.create(
            id="e295ca17-c6de-4d44-b003-ffefefa7a805",
            user_id=1,
            name="Old Doc",
            body="Old Content",
        )

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "e295ca17-c6de-4d44-b003-ffefefa7a805",
                "user_id": 1,
                "name": "Updated Doc",
                "body": "Updated Content",
            }
        ]

        sync_user_documents("fake_token")

        # Check if the document was updated
        doc = UserDocument.objects.get(id="e295ca17-c6de-4d44-b003-ffefefa7a805")
        self.assertEqual(doc.name, "Updated Doc")
        self.assertEqual(doc.body, "Updated Content")
        self.assertEqual(doc.user_id, 1)

    @patch("documents.tasks.requests.get")
    def test_sync_user_documents_does_nothing_on_api_failure(self, mock_get):
        """Test if the function does nothing when API request fails."""
        mock_get.return_value.status_code = 500

        sync_user_documents("fake_token")

        # Database should still be empty
        self.assertEqual(UserDocument.objects.count(), 0)

    @patch("documents.tasks.requests.get")
    def test_sync_user_documents_handles_empty_response(self, mock_get):
        """Test if no documents are created when API returns an empty list."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        sync_user_documents("fake_token")

        # Database should still be empty
        self.assertEqual(UserDocument.objects.count(), 0)
