from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("doctors", DoctorViewSet)
router.register("categories", CategoryViewSet)
router.register("comments", CommentViewSet)
router.register("services", ServiceViewSet)
router.register("appointments", AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('toggle_like/<int:d_id>/', toggle_like),
    path('add_rating/<int:d_id>/', add_rating),
    path('add_to_favorites/<int:d_id>/', add_to_favorites),
    path('my_favorites/', my_favorites),
]
