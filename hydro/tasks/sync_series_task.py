import traceback
from celery import shared_task
from hydro.models import State, Station, PrecipitationRecord, TaskReport


@shared_task(bind=True)
def run_precipitation_sync_pipeline(self, task_report_id, state_filter=None):
    """
    Pipeline principal para sincronização assíncrona de séries históricas pluviométricas.
    """

    try:
        report = TaskReport.objects.get(id=task_report_id)
        # celery pega o trabalho no banco de dados

        report.status = TaskReport.StatusChoices.PROCESSING
        # mudando o status do trabalho para processando

        report.task_id = self.request.id 
        # identificação do trabalho
        
        report.save()
        

    except TaskReport.DoesNotExist:
        return "Error: TaskReport não encontrado."

    try:
        if not state_filter:
            selected_states = State.objects.all()
            # Definição do Escopo (Filtro): Se a lista estiver vazia: O sistema consulta a entidade State e recupera todos os estados. 

        else:
            selected_states = State.objects.filter(name__in=state_filter)
            # Definição do Escopo (Filtro): Buscou no banco de dados todas as estações selecionadas.

        station_queryset = Station.objects.filter(
            state__in=selected_states
        )
        # Estações meteorologicas dentro dos estados selecionados

        set_station_codes: list[str] = list(station_queryset.values_list('code', flat=True))
        # Conjunto de codigos das estações

        del selected_states
        # Liberando espaço de memoria

        if not set_station_codes:
            report.status = TaskReport.StatusChoices.SUCCESS
            report.result_message = "Nenhuma estação encontrada para os estados informados."
            report.save()
            return report.result_message

        CHUNK_SIZE: int = 3

        batches = [
            set_station_codes[i:i+CHUNK_SIZE] for i in range(0, len(set_station_codes), CHUNK_SIZE)
        ]
        # Separação de cada lote

        print(f"Há {len(batches)} lotes para processamento.")

        for batch in batches:
            # Chamada do service de processamento que comunica com o hydrobr
            pass

    except Exception as e:
        if 'report' in locals():
            report.status = TaskReport.StatusChoices.FAILED
            report.error_log = traceback.format_exc()
            report.result_message = str(e)
            report.save()
        raise e