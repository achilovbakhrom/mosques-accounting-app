"""
URL mappings for the unit API.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from record import views

app_name = 'record'

router = DefaultRouter()
router.register('', views.RecordView)

urlpatterns = router.urls

