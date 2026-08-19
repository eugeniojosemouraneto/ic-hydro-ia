from django.core.management.base import BaseCommand

from hydro.pipelines import StationANAPipeline, StationINMETPipeline


class Command(BaseCommand):

    help = 'Executa o pipeline de ingestão de estações meteorológicas inéditas da ANA'

    def handle(self, *args, **kwargs):
        # Feedback visual no terminal para o usuário saber que o processo começou
        self.stdout.write(self.style.WARNING('Iniciando comunicação com a API da hydrobr... Isso pode levar alguns segundos.'))
        
        try:

            StationANAPipeline.populate_ana_stations()

            StationINMETPipeline.match_inmet_stations()

            self.stdout.write(self.style.SUCCESS(f'[SUCESSO] Pipeline finalizado!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERRO CRÍTICO] Falha na execução do pipeline: {str(e)}'))