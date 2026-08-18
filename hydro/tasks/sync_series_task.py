import traceback
import logging
from celery import shared_task
from hydro.models import State, Station, PrecipitationRecord, TaskReport
from hydro.service import  fetch_and_process_precipitation


logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_precipitation_sync_pipeline(self, task_report_id, state_filter=None):
    """
    Pipeline principal para sincronização assíncrona de séries históricas pluviométricas.
    """
    print(f"Log [ hydro/tasks/sync_series_task.py - metodo run_+precipitation_sync_pipeline ] - Inicio")


    logger.info(f"[Início] Task disparada! ID do Relatório: {task_report_id} | Filtro de Estados: {state_filter}")

    try:
        report = TaskReport.objects.get(id=task_report_id)
        # celery pega o trabalho no banco de dados

        report.status = TaskReport.StatusChoices.PROCESSING
        # mudando o status do trabalho para processando

        report.task_id = self.request.id 
        # identificação do trabalho
        
        report.save()

        logger.info(f"[Auditoria] TaskReport ({task_report_id}) atualizado para PROCESSING. Celery Task ID: {self.request.id}")
        

    except TaskReport.DoesNotExist:
        logger.error(f"[Erro] TaskReport com ID {task_report_id} não encontrado no banco de dados.")

        return "Error: TaskReport não encontrado."

    try:
        if not state_filter:
            selected_states = State.objects.all()
            # Definição do Escopo (Filtro): Se a lista estiver vazia: O sistema consulta a entidade State e recupera todos os estados. 

            logger.info("[Escopo] Nenhum filtro aplicado. Consultando ALL (todos os estados).")

        else:
            selected_states = State.objects.filter(name__in=state_filter)
            # Definição do Escopo (Filtro): Buscou no banco de dados todas as estações selecionadas.

            logger.info(f"[Escopo] Filtro aplicado. Consultando apenas os estados: {state_filter}")

        station_queryset = Station.objects.filter(
            state__in=selected_states
        )
        # Estações meteorologicas dentro dos estados selecionados

        list_station_codes: list[str] = list(station_queryset.values_list('code', flat=True))
        # Conjunto de codigos das estações

        logger.info(f"[Extração] Encontradas {len(list_station_codes)} estações vinculadas a esses estados.")

        del selected_states
        # Liberando espaço de memoria

        if not list_station_codes:
            report.status = TaskReport.StatusChoices.SUCCESS
            report.result_message = "Nenhuma estação encontrada para os estados informados."
            report.save()

            logger.warning("[Fim] Nenhuma estação para processar. Encerrando pipeline prematuramente.")

            return report.result_message

        CHUNK_SIZE: int = 3

        batches = [
            list_station_codes[i:i+CHUNK_SIZE] for i in range(0, len(list_station_codes), CHUNK_SIZE)
        ]

        total_entered: int = 0
        index: int = 0
        
        # Separação de cada lote

        logger.info(f"[Particionamento] As {len(list_station_codes)} estações foram divididas em {len(batches)} lotes (chunks) de {CHUNK_SIZE}.")

        for batch in batches:
            index += CHUNK_SIZE
            # 5.1. Chamada do Serviço Externo (Encapsulado)
            # Ele recebe [code1, code2, code3, code4] e devolve uma lista de dicionários prontos
            processed_data_dicts = fetch_and_process_precipitation(batch, index)

            if processed_data_dicts:
                records_to_create = [PrecipitationRecord(**data) for data in processed_data_dicts]

                PrecipitationRecord.objects.bulk_create(
                    records_to_create,
                    batch_size=2000,
                    ignore_conflicts=True 
                )

                total_entered += len(records_to_create)

        logger.info("[Sucesso] Todos os lotes foram despachados com sucesso!")

        report.status = TaskReport.StatusChoices.SUCCESS
        report.result_message = f"Sincronização concluída com sucesso. {total_entered} novos registros pluviométricos inseridos."
        report.save()

        return report.result_message

    except Exception as e:
        logger.error(f"[Falha Crítica] O pipeline quebrou com a seguinte exceção: {str(e)}")
        
        if 'report' in locals():
            report.status = TaskReport.StatusChoices.FAILED
            report.error_log = traceback.format_exc()
            report.result_message = str(e)
            report.save()
        raise e