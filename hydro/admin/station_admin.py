from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from hydro.models import Station

@admin.register(Station)
class StationAdmin(GISModelAdmin):
    """
    Configuração do painel administrativo para as Estações com PostGIS.
    Agora exibe a identificação unificada (ANA e INMET).
    """
    list_display = ('code_ana', 'code_inmet', 'name', 'state', 'city', 'station_type', 'latitude', 'longitude')
    search_fields = ('code_ana', 'code_inmet', 'name', 'city')
    list_filter = ('state', 'station_type')
    ordering = ('state', 'name')