from django.urls import path
from hydro.views import sync_series_page, start_sync_task, check_task_status, station_map_page, api_get_stations, station_dashboard_view

app_name = 'hydro'

urlpatterns = [
    # User
    path('sync-series/', sync_series_page, name='sync_series_page'),
    path('map/', station_map_page, name='station_map_page'),
    path('estacao/<str:station_code>/', station_dashboard_view, name='station_dashboard_view'),

    # API
    path('api/sync-series/start/', start_sync_task, name='start_sync_task'),
    path('api/sync-series/status/<int:report_id>/', check_task_status, name='check_task_status'),
    path('api/stations/', api_get_stations, name='api_get_stations')
]