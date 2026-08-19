import logging
import pandas 
import hydrobr

from django.contrib.gis.geos import Point
from hydro.models import Station


# Configuração do Log de Sistema 
logger = logging.getLogger('hydro_system')

class StationANAPipeline:
    """
    Este pipeline vai administrar um fluxo de ETL (Extração, Transformação e Carga) 
    das estações meteorológicas da agência ANA. 
    """

    @staticmethod
    def populate_ana_stations() -> int:
        """
        Executa a busca de estações na API, filtra as inéditas via conjuntos matemáticos,
        valida coordenadas espaciais e salva no banco de dados PostGIS.
        
        Returns:
            int: O número de novas estações inseridas com sucesso no banco de dados.
        """

        logger.info("[ INFO ] Iniciando pipeline de ingestão de estação ANAF.")

        # Etapa 1.0. - Extração, executa a conexão com a agência ANA e retorna um pandas DataFrame.
        dataframe_api_stations: pandas.DataFrame = hydrobr.get_data.ANA.list_prec_stations(source='ANAF')

        logger.info(f"[ INFO ] Extração DataFrame API Stations: {dataframe_api_stations.size} elementos.")

        # Etapa 2.0. - Conjunto (set[str]) dos códigos de estações da API.
        set_api_stations: set[str] = set(dataframe_api_stations['Code'].astype(str))

        # Etapa 3.0. - Conjunto (set[str]) dos códigos de estação do Banco de dados.
        set_database_stations: set[str] = set(
            Station.objects.values_list('code', flat=True)
        ) 

        logger.info(f"[ INFO ] Extração Conjunto Banco de Dados Stations: {len(set_database_stations)} elementos.")

        # Etapa 4.0. - Diferença de matemática conjuntos O(1) para encontrar estações inéditas.
        set_unreleased_codes: set[str] = set_api_stations - set_database_stations

        logger.info(f"[ INFO ] Conjunto Stations ineditas: {len(set_database_stations)} elementos.")

        if not set_unreleased_codes:
            logger.info("[ INFO ] Nenhuma estação inédita ao banco de dados encontrada na API.")
            return 0

        # Etapa 5.0. - Descartar da memória o conjunto do banco de dados.
        del set_database_stations

        # Etapa 6.0. - Separa do DataFrame original vindo da API os dados das estações inéditas.
        dataframe_unreleased_stations: pandas.DataFrame = dataframe_api_stations[
            dataframe_api_stations['Code'].astype(str).isin(set_unreleased_codes)
        ].copy()

        logger.info(f"[ INFO ] Aquisição Dataframe Stations ineditas: {dataframe_unreleased_stations.size} elementos.")

        # Etapas 7.0. e 8.0. - Descarte da memória o DataFrame original vindo da API e o conjunto da API.
        del dataframe_api_stations
        del set_api_stations

        # Etapa 9.0. - Validação espacial das estações ineditas.
        valid_stations_instances: list[Station] = []

        for station_code, row_data in dataframe_unreleased_stations.iterrows():
            station_code: str = str(row_data.get('Code'))
            lat: float = row_data.get('Latitude')
            lon: float = row_data.get('Longitude')

            # Verificação contra nulos e limites geográficos absolutos
            is_lat_valid: bool = pandas.notna(lat) and (-90.0 <= lat <= 90.0)
            is_lon_valid: bool = pandas.notna(lon) and (-180.0 <= lon <= 180.0)

            if not (is_lat_valid and is_lon_valid):
                logger.warning(
                    f"[WARNING] Estação {station_code} descartada por coordenadas inválidas: ({lat}, {lon})"
                )
                continue

            point: Point = Point(
                float(lon),
                float(lat)
            )

            valid_stations_instances.append(
                Station(
                    code=station_code,
                    name=str(row_data.get('Name', 'Sem Nome')),
                    city=str(row_data.get('City', '')),
                    state=str(row_data.get('State', '')),
                    geom=point
                )
            )

        # Etapa 10.0. - Persistencia de dados 
        if valid_stations_instances:
            Station.objects.bulk_create(valid_stations_instances)
            logger.info(f"[INFO] {len(valid_stations_instances)} estações inéditas salvas com sucesso.")
            
        return len(valid_stations_instances)