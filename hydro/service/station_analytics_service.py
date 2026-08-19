from django.db.models import Count, Min, Max, Q
from django.core.paginator import Paginator

from hydro.models import Station, PrecipitationRecord


def get_station_statistics(station: Station) -> dict:
    """Calcula os metadados e agregações matemáticas de uma estação."""

    stats = PrecipitationRecord.objects.filter(station=station).aggregate(
        total_records=Count('id'),
        total_gaps=Count('id', filter=Q(is_gap=True)),
        start_date=Min('date'),
        end_date=Max('date')
    )
    return stats

def get_paginated_historical_series(
    station: Station, filters: dict, page_number: int = 1
): 
    """Aplica filtros de data/gap e retorna uma página específica da série histórica."""

    historical_series = PrecipitationRecord.objects.filter(station=station)

    if filters.get('date'):
        historical_series = historical_series.filter(date=filters['date'])

    if filters.get('only_gaps') == 'true':
        historical_series = historical_series.filter(is_gap=True)

    ordering = filters.get('ordering', '-date')

    historical_series = historical_series.order_by(ordering)

    paginator = Paginator(historical_series, 50)

    return paginator.get_page(page_number)

def get_paginated_gaps_only(station: Station, page_number: int = 1):
    """Retorna exclusivamente os registros marcados como falha (gap) para auditoria."""

    gaps_queryset = PrecipitationRecord.objects.filter(
        station=station,
        is_gap=True
    ).order_by('-date')

    paginator = Paginator(gaps_queryset, 50)

    return paginator.get_page(page_number)

def build_station_dashboard_payload(station_code: str, filters: dict, page_series: int, page_gaps: int) -> dict:
    """Atua como um 'Facade', unindo os três serviços atômicos para entregar um pacote completo para a View da Dashboard."""

    station = Station.objects.get(code=station_code)

    return {
        'station': station,
        'stats': get_station_statistics(station),
        'series_page': get_paginated_historical_series(station, filters, page_series),
        'gaps_page': get_paginated_gaps_only(station, page_gaps),
    }