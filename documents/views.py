from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import UserDocument
from .serializers import UserDocumentSerializer
from .authentication import LiveViewAuth
from .tasks import sync_user_documents
from drf_yasg.utils import swagger_auto_schema


class UserDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """Fetch user documents and trigger async update"""

    serializer_class = UserDocumentSerializer
    authentication_classes = [LiveViewAuth]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter documents by the user_id from the token payload."""
        token_payload = self.request.auth
        user_id = token_payload.get("user_id")

        if not user_id:
            return UserDocument.objects.none()

        return UserDocument.objects.filter(user_id=user_id)

    @swagger_auto_schema(
        operation_description="List all user documents and trigger an async sync task.",
        responses={200: UserDocumentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        sync_user_documents.delay(request.auth["key"])

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
