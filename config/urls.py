from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.api_router import router

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication & Accounts
    path("api/auth/", include("apps.accounts.urls")),
    # Campaigns (existing)
    path("api/campaigns/", include("apps.campaigns.urls")),
    # All new API endpoints (agents, leads, calls, webhooks, integrations, exports)
    path("api/", include(router.urls)),
    # Schema & Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
