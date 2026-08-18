from django.shortcuts import render
from django.http import JsonResponse
from hydro.models import Station, State


def station_map_page(request):
    """
    Renderiza a página principal do mapa interativo com o filtro de estados.
    """
    states: list[State] = State.objects.all().order_by('name')
    print(f"\n\n\n\n{len(states)}\n\n\n")
    return render(
        request,
        'hydro/map_page.html',
        context={
            'states': states
        }
    )

def api_get_stations(request):
    """
    API interna que retorna os metadados e coordenadas das estações em JSON.
    Aceita o parâmetro 'state' para filtragem.
    """
    state_filter = request.GET.get('state')

    stations_queryset = Station.objects.select_related('state').all()

    if state_filter:
        stations_queryset = stations_queryset.filter(state__name=state_filter)

    stations_data = stations_queryset.values(
        'code', 'name', 'city', 'state__name', 'geom'
    )

    features = []
    for station in stations_data:
        if station['geom']:
            features.append({
                'code': station['code'],
                'name': station['name'],
                'city': station['city'] or 'N/A',
                'state': station['state__name'] or 'N/A',
                'lat': station['geom'].y,
                'lng': station['geom'].x,
            })

    print(f"\n\n\n\n{len(features)}\n\n\n")

    return JsonResponse({
        'stations': features
    })