from django.urls import path

from .views import DashboardAPIView

app_name = "dashboard-api"
urlpatterns = [path("resumen/", DashboardAPIView.as_view(), name="resumen")]
