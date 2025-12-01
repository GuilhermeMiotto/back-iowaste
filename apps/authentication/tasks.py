from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Log


@shared_task
def cleanup_old_logs():
    """Remove logs com mais de 90 dias"""
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count, _ = Log.objects.filter(data__lt=cutoff_date).delete()
    return f'Removidos {deleted_count} logs antigos'
