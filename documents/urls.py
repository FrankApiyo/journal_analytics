from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDocumentViewSet

router = DefaultRouter()
router.register(r"user_documents", UserDocumentViewSet, basename="user_documents")

urlpatterns = [
    path("", include(router.urls)),
]
