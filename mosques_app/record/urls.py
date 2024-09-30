"""
URL mappings for the unit API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from record import views

app_name = 'record'

router = DefaultRouter()
router.register('', views.RecordView)

urlpatterns = [
    path('', include(router.urls), name='place-list'),
]

