from django.urls import path
from rest_framework import routers
from .views import EventViewSet, ReservationViewSet

router = routers.DefaultRouter()

router.register(r'events', EventViewSet, basename='event')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = router.urls