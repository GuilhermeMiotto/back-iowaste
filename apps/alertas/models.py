from django.db import models
from apps.bombonas.models import Bombona


class Alerta(models.Model):
    """Modelo de Alerta de Bombonas"""
    
    TIPO_CHOICES = [
        ('nivel_alto', 'Nível Alto'),
        ('nivel_critico', 'Nível Crítico'),
        ('temperatura_alta', 'Temperatura Alta'),
        ('manutencao', 'Manutenção Necessária'),
        ('sensor_falha', 'Falha no Sensor'),
        ('outros', 'Outros'),
    ]
    
    NIVEL_CHOICES = [
        ('baixo', 'Baixo'),
        ('medio', 'Médio'),
        ('alto', 'Alto'),
        ('critico', 'Crítico'),
    ]
    
    # Bombona relacionada
    bombona = models.ForeignKey(
        Bombona,
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name='Bombona'
    )
    
    # Informações do alerta
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        verbose_name='Nível'
    )
    descricao = models.TextField(verbose_name='Descrição')
    
    # Status
    resolvido = models.BooleanField(default=False, verbose_name='Resolvido')
    data_resolucao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Resolução'
    )
    observacoes_resolucao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações da Resolução'
    )
    
    # Controle
    data_alerta = models.DateTimeField(auto_now_add=True, verbose_name='Data do Alerta')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-data_alerta']
        indexes = [
            models.Index(fields=['-data_alerta']),
            models.Index(fields=['bombona']),
            models.Index(fields=['resolvido']),
            models.Index(fields=['nivel']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.bombona.identificacao} - {self.data_alerta.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def nivel_color(self):
        """Retorna cor do nível de alerta"""
        colors = {
            'baixo': 'blue',
            'medio': 'yellow',
            'alto': 'orange',
            'critico': 'red',
        }
        return colors.get(self.nivel, 'gray')
