from django.urls import path
from . import views

app_name = 'place'


urlpatterns = [
    path('', views.PlaceView.as_view(), name='place-list'),
    path('mosque_autocomplete/', views.PlaceViewMosques.as_view(), name='place-autocomplete'),
    path('<int:id>/', views.PlaceDetailView.as_view(), name='place-detail'),
]
