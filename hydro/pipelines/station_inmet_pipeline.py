import logging
import pandas
import hydrobr

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from hydro.models import Station


logger = logging.getLogger('hydro_system')

class StationINMETPipeline:
    """
    Pipeline responsável por cruzar e vincular os códigos das estações do INMET
    às estações da ANA já existentes no banco de dados espacial (PostGIS).
    """

    @staticmethod
    def match_inmet_stations(radius_km: float = 50.0) -> int:
        logger.info("[ INFO ] Iniciando busca de estações INMET para pareamento espacial.")

        inmet_dataframe: pandas.DataFrame = hydrobr.get_data.INMET.list_stations(station_type='both')

        logger.info(f"[ INFO ] Encontradas {len(inmet_dataframe)} estações no inventário do INMET.")

        matched_count: int = 0

        stations_to_update: list[Station] = []

        for _, row in inmet_dataframe.iterrows():
            inmet_code: str = str(row.get('Code'))

            latitude: float = row.get('Latitude')
            longitude: float = row.get('Longitude')

            is_lat_valid: bool = pandas.notna(latitude) and (-90.0 <= latitude <= 90.0)
            is_lon_valid: bool = pandas.notna(longitude) and (-180.0 <= longitude <= 180.0)

            if not (is_lat_valid and is_lon_valid):
                continue

            inmet_point: Point = Point(float(longitude), float(latitude), srid=4326)

            closest_ana = Station.objects.filter(
                code_inmet__isnull=True,
                geom__distance_lte=(inmet_point, D(km=radius_km))
            ).annotate(
                distance=Distance('geom', inmet_point)
            ).order_by('distance').first()

            if closest_ana:
                closest_ana.code_inmet = inmet_code
                stations_to_update.append(closest_ana)
                matched_count += 1

        if stations_to_update:
            Station.objects.bulk_update(stations_to_update, ['code_inmet'], batch_size=1000)
            logger.info(f"[ SUCESSO ] {matched_count} estações da ANA foram pareadas com o INMET com sucesso.")
            
        else:
            logger.info("[ INFO ] Nenhum novo pareamento possível no momento.")

        return matched_count