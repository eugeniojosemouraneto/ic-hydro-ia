import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from hydro.models import State, TaskReport
from hydro.tasks import run_precipitation_sync_pipeline


# FASE 1: O Primeiro Contato (Carregamento da Página)
def sync_series_page(request):
    """
    Renderiza a página principal com o formulário de estados.
    """
    states = State.objects.all().order_by('name')
    
    return render(
        request, 
        'hydro/sync_page.html', 
        {
            'states': states
        }
    )


# FASE 3: A Reação do Servidor (View de Gatilho)
@require_POST
def start_sync_task(request):
    """
    Recebe a requisição assíncrona (AJAX), cria o TaskReport e dispara o Celery.
    """
    print(f"Log [ hydro/views/sync_view.py - metodo start_sync_task ] - Iniciando!")

    try:
        data = json.loads(request.body)
        
        selected_states = data.get('states', [])

        print(f"Log [ hydro/views/sync_view.py - metodo start_sync_task ] - Aquisição dos estados\nStates: {selected_states}")

    except json.JSONDecodeError:
        return JsonResponse(
            {
                'error': 'Payload inválido.'
            }, 
            status=400
        )

    report = TaskReport.objects.create(
        task_id=str(uuid.uuid4()),
        task_name='Sincronização de Séries Pluviométricas',
        status=TaskReport.StatusChoices.PENDING,
        user=request.user if request.user.is_authenticated else None
    )

    print(f"Log [ hydro/views/sync_view.py - metodo start_sync_task ] - Criado o report com sucesso!")
    # Despacha o trabalho para o Celery em segundo plano usando .delay()
    # Importante: A nossa Task já sabe que se selected_states for vazia, ela deve buscar todos os estados.
    print(f"Log [ hydro/views/sync_view.py - metodo start_sync_task ] - Chamando a task run_precipitation_sync_pipeline")
    run_precipitation_sync_pipeline.delay(
        task_report_id=report.id,
        state_filter=selected_states
    )

    # Devolve uma resposta IMEDIATA para o navegador com o ID do relatório
    return JsonResponse(
        {'task_report_id': report.id}, 
        status=202
    )


# FASE 4 (Bastidores): A View de Status (Long Polling)
def check_task_status(request, report_id):
    """
    View de consulta contínua. O JavaScript bate aqui a cada X segundos para saber se a task terminou.
    """
    try:
        report = TaskReport.objects.get(id=report_id)
        
        # Retorna o status atual e possíveis mensagens ou logs de erro
        return JsonResponse({
            'status': report.status,
            'result_message': report.result_message,
            'error_log': report.error_log
        }, status=200)
        
    except TaskReport.DoesNotExist:
        return JsonResponse({'error': 'Relatório não encontrado.'}, status=404)