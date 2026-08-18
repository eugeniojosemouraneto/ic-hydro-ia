import time
import logging
import pandas
import hydrobr
from django.db.models import Max
from hydro.models import PrecipitationRecord


logger = logging.getLogger(__name__)

def fetch_and_process_precipitation(station_codes: list[str], index: int) -> list[dict]:
    """
    Serviço especialista para extração e transformação (ETL) de séries históricas.
    """

    MAX_ATTEMPTS: int = 3

    dataframe_api = None

    logger.info(f"[Serviço] Iniciando extração para {len(station_codes)} estações. Já passou {index} chunks.")

    for i in range(MAX_ATTEMPTS + 1):
        try:
            dataframe_api = hydrobr.get_data.ANA.prec_data(station_codes)
            logger.info("[Serviço] Conexão com a API bem-sucedida.")
            break 
            
        except Exception as e:
            logger.warning(f"[Serviço] Falha na API (Tentativa {i}/{MAX_ATTEMPTS}): {e}")
            if MAX_ATTEMPTS == i:
                logger.error("[Serviço] Máximo de tentativas atingido. Abortando lote.")
                raise Exception("Falha crítica de comunicação com a API da HydroBR.")
            
            logger.info("[Serviço] Aguardando 60 segundos antes da próxima tentativa...")
            time.sleep(60)

    if dataframe_api is None or dataframe_api.empty:
        logger.warning("[Serviço] A API não retornou dados para este lote.")
        return []

    formatted_dataframe: pandas.DataFrame = dataframe_api.reset_index().melt(
        id_vars=['index'],
        var_name='station_id',  # Usamos station_id para parear com a ForeignKey do Django
        value_name='value'      # Nome exato da coluna de precipitação no models.py
    )
    formatted_dataframe.rename(columns={'index': 'date'}, inplace=True)

    formatted_dataframe['date'] = pandas.to_datetime(formatted_dataframe['date'])

    latest_dates = PrecipitationRecord.objects.filter(
        station_id__in=station_codes
    ).values('station_id').annotate(latest_date=Max('date'))

    if latest_dates:
        dataframe_latest = pandas.DataFrame(list(latest_dates))
        dataframe_latest['latest_date'] = pandas.to_datetime(dataframe_latest['latest_date'])

        formatted_dataframe = formatted_dataframe.merge(
            dataframe_latest,
            on='station_id',
            how='left'
        )
        formatted_dataframe = formatted_dataframe[
            (formatted_dataframe['latest_date'].isna()) | (formatted_dataframe['date'] > formatted_dataframe['latest_date'])
        ]
        formatted_dataframe.drop(columns=['latest_date'], inplace=True)

    formatted_dataframe['is_gap'] = formatted_dataframe['value'].isna()

    # O Django ORM espera o valor 'None' do Python no lugar do 'NaN' do Pandas para colunas nulas
    formatted_dataframe['value'] = formatted_dataframe['value'].astype(object).where(formatted_dataframe['value'].notna(), None)
    
    # Previne erros de fuso horário garantindo que a data seja nativa do Python e sem timezone (date object)
    formatted_dataframe['date'] = formatted_dataframe['date'].dt.date

    logger.info(f"[Serviço] Filtragem concluída. Devolvendo {len(formatted_dataframe)} novos registros inéditos.")
    
    # Converte o DataFrame limpo em uma lista de dicionários nativos do Python
    return formatted_dataframe.to_dict('records')