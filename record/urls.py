"""
URL mappings for the unit API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from record import views

app_name = 'record'

router = DefaultRouter()
router.register('', views.RecordView, basename="records")
# router.register('report/', views.RecordReportView, basename="report")

urlpatterns = [
    path('', include(router.urls)),
    path('report/<str:period>/', views.RecordReportView.as_view(), name="report"),
    path('report-hierarchicallly/<str:period>/', views.RecordHierarchicallyReportView.as_view(), name="report"),
    path('report-profit/<int:place_id>/', views.ReportProfitView.as_view(), name="profit"),
]

