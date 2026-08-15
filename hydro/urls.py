from django.urls import path
from hydro.views import sync_series_page, start_sync_task, check_task_status

app_name = 'hydro'

urlpatterns = [
    # User
    path('sync-series/', sync_series_page, name='sync_series_page'),

    # API
    path('api/sync-series/start/', start_sync_task, name='start_sync_task'),
    path('api/sync-series/status/<int:report_id>/', check_task_status, name='check_task_status'),
]