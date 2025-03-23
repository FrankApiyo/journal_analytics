from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from .models import UserDocument
from .serializers import UserDocumentSerializer
from .authentication import LiveViewAuth
from .tasks import sync_user_documents


class UserDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """Fetch user documents and trigger async update"""

    queryset = UserDocument.objects.all()
    serializer_class = UserDocumentSerializer
    authentication_classes = [LiveViewAuth]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Trigger async task to sync documents
        sync_user_documents.delay(request.auth)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
