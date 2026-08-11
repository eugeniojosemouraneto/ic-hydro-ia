from django.core.management.base import BaseCommand

from hydro.pipelines import StationPipeline


class Command(BaseCommand):

    help = 'Executa o pipeline de ingestão de estações meteorológicas inéditas da ANA'

    def handle(self, *args, **kwargs):
        # Feedback visual no terminal para o usuário saber que o processo começou
        self.stdout.write(self.style.WARNING('Iniciando comunicação com a API da hydrobr... Isso pode levar alguns segundos.'))
        
        try:
            new_stations: int = StationPipeline.populate_stations()

            if new_stations > 0:
                self.stdout.write(self.style.SUCCESS(f'[SUCESSO] Pipeline finalizado! {new_stations} novas estações foram inseridas no banco PostGIS.'))
            else:
                self.stdout.write(self.style.SUCCESS('[SUCESSO] Pipeline finalizado! O banco de dados já está 100% atualizado. Nenhuma estação inédita encontrada.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERRO CRÍTICO] Falha na execução do pipeline: {str(e)}'))