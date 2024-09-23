from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'place'

router = DefaultRouter()

router.register('', views.PlaceView)

urlpatterns = [
    path('', include(router.urls)),
]
