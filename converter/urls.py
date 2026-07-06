from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('converter/', views.converter_terminal_view, name='terminal'),
    path('convert/', views.convert_file_view, name='convert_file'),
    path('success/<int:history_id>/', views.success_view, name='success'),
    path('history/', views.history_page_view, name='history_page'),
    path('download/<int:doc_id>/', views.download_file_view, name='download'),
    path('clear-notification/<int:note_id>/', views.clear_notification_view, name='clear_notification'),
]
