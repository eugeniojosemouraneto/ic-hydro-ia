from django.shortcuts import render, get_object_or_404

from hydro.models import Station
from hydro.service import build_station_dashboard_payload


def station_dashboard_view(request, station_code):
    """
    View que renderiza a Dashboard de uma estação específica.
    Atua como controlador HTTP, delegando a lógica de negócio para a camada de Serviço.
    """

    get_object_or_404(Station, code=station_code)

    filters = {
        'date': request.GET.get('date'),
        'only_gaps': request.GET.get('only_gaps'),
        'ordering': request.GET.get('ordering', '-date')
    }

    page_series = request.GET.get('page_series', 1)
    page_gaps = request.GET.get('page_gaps', 1)

    dashboard_data = build_station_dashboard_payload(
        station_code=station_code,
        filters=filters,
        page_series=page_series,
        page_gaps=page_gaps
    )

    return render(
        request=request,
        template_name='hydro/station_dashboard.html',
        context=dashboard_data
    )