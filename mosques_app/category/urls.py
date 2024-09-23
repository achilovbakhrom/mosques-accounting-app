from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'category'

router = DefaultRouter()

router.register('', views.CategoryView)

urlpatterns = [
    path('', include(router.urls)),
]
