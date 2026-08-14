import os
from celery import Celery

# Define o módulo de configurações padrão do Django para o programa Celery.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Lê as configurações do Celery a partir do settings.py (tudo que começar com CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega automaticamente as tarefas (tasks.py) de todos os apps instalados (como o app 'hydro')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')