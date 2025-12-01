from celery import shared_task
from .simulator import simulator


@shared_task
def simulate_iot_readings():
    """Task Celery para simular leituras IoT periodicamente"""
    resultado = simulator.simular_todas_bombonas()
    return f"Simulação concluída: {resultado}"


@shared_task
def reset_full_bombonas():
    """Task para resetar bombonas cheias automaticamente"""
    from apps.bombonas.models import Bombona
    
    bombonas_cheias = Bombona.objects.filter(status='cheia')
    count = 0
    
    for bombona in bombonas_cheias:
        simulator.resetar_bombona(bombona)
        count += 1
    
    return f"{count} bombonas resetadas"
