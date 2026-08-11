from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Station

@admin.register(Station)
class StationAdmin(GISModelAdmin):
    """
    Configuração do painel administrativo para as Estações.
    Utiliza GISModelAdmin para renderizar automaticamente um mapa interativo 
    no campo 'geom' baseado em Leaflet/OpenStreetMap.
    """
    # Quais colunas vão aparecer na lista principal
    list_display = ('code', 'name', 'state', 'city', 'station_type', 'latitude', 'longitude')
    
    # Adiciona uma barra de pesquisa
    search_fields = ('code', 'name', 'city')
    
    # Adiciona filtros laterais
    list_filter = ('state', 'station_type')
    
    # Define a ordenação padrão no admin
    ordering = ('state', 'name')