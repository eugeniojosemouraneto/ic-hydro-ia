from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from hydro.models import Station

@admin.register(Station)
class StationAdmin(GISModelAdmin):
    """
    Configuração do painel administrativo para as Estações com PostGIS.
    """
    list_display = ('code', 'name', 'state', 'city', 'station_type', 'latitude', 'longitude')
    search_fields = ('code', 'name', 'city')
    list_filter = ('state', 'station_type')
    ordering = ('state', 'name')