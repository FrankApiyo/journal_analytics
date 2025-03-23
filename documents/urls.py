from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import UserDocumentViewSet

# Schema view for Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="User Documents API",
        default_version="v1",
        description="API for fetching and syncing user documents",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r"user_documents", UserDocumentViewSet, basename="user_documents")


urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
