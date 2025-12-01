import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('iowaste')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuração de tarefas periódicas
app.conf.beat_schedule = {
    'simulate-iot-data-every-5-minutes': {
        'task': 'apps.simulator.tasks.simulate_iot_readings',
        'schedule': 300.0,  # 5 minutos
    },
    'cleanup-old-logs-daily': {
        'task': 'apps.authentication.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0),  # Às 3h da manhã
    },
}
