"""
URL mappings for the unit API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from unit import views

app_name = 'unit'

router = DefaultRouter()

router.register('', views.UnitView)

urlpatterns = [
    path('', include(router.urls)),
]
