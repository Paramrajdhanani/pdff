from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('v1/convert/', views.APIConvertView.as_view(), name='api_convert'),
    path('v1/history/', views.APIHistoryView.as_view(), name='api_history'),
]
