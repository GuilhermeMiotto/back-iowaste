from django.db import models
from django.contrib.auth import get_user_model
from apps.bombonas.models import Bombona

User = get_user_model()


class Coleta(models.Model):
    """Modelo de Coleta de Resíduos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Bombona coletada
    bombona = models.ForeignKey(
        Bombona,
        on_delete=models.CASCADE,
        related_name='coletas',
        verbose_name='Bombona'
    )
    
    # Responsável pela coleta
    operador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coletas',
        verbose_name='Operador'
    )
    
    # Dados da coleta
    data_coleta = models.DateTimeField(verbose_name='Data da Coleta')
    peso_coletado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Peso Coletado (kg)'
    )
    
    # Destino
    destino = models.CharField(
        max_length=300,
        verbose_name='Destino',
        help_text='Local para onde os resíduos foram enviados'
    )
    empresa_destino = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Empresa de Destino'
    )
    
    # Status e observações
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    # Documentação
    numero_manifesto = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número do Manifesto'
    )
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Coleta'
        verbose_name_plural = 'Coletas'
        ordering = ['-data_coleta']
        indexes = [
            models.Index(fields=['-data_coleta']),
            models.Index(fields=['bombona']),
            models.Index(fields=['operador']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Coleta {self.id} - {self.bombona.identificacao} - {self.data_coleta.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        """Atualizar peso da bombona após coleta concluída"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.status == 'concluida' and not is_new:
            # Reduzir peso da bombona
            if self.bombona.peso_atual >= self.peso_coletado:
                self.bombona.peso_atual -= self.peso_coletado
                self.bombona.atualizar_status()
