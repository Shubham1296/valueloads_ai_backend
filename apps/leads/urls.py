from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, LeadImportBatchViewSet, LeadNoteViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'import-batches', LeadImportBatchViewSet, basename='leadimportbatch')
router.register(r'notes', LeadNoteViewSet, basename='leadnote')

urlpatterns = [
    path('', include(router.urls)),
]
