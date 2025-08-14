from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkOrderViewSet, WorkOrderPhotoViewSet, WorkOrderDocumentViewSet,
    WorkOrderCommentViewSet, WorkOrderChecklistViewSet, WorkOrderChecklistItemViewSet
)

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet)
router.register(r'photos', WorkOrderPhotoViewSet)
router.register(r'documents', WorkOrderDocumentViewSet)
router.register(r'comments', WorkOrderCommentViewSet)
router.register(r'checklists', WorkOrderChecklistViewSet)
router.register(r'checklist-items', WorkOrderChecklistItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]