from django.db import models
from apps.empresas.models import Empresa


class Bombona(models.Model):
    """Modelo de Bombona de Resíduos"""
    
    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('quase_cheia', 'Quase Cheia'),
        ('cheia', 'Cheia'),
        ('manutencao', 'Manutenção'),
        ('inativa', 'Inativa'),
    ]
    
    TIPO_RESIDUO_CHOICES = [
        ('hospitalar_infectante', 'Hospitalar Infectante (Classe A)'),
        ('hospitalar_quimico', 'Hospitalar Químico (Classe B)'),
        ('hospitalar_radioativo', 'Hospitalar Radioativo (Classe C)'),
        ('hospitalar_perfurocortante', 'Hospitalar Perfurocortante (Classe E)'),
        ('industrial_toxico', 'Industrial Tóxico'),
        ('solventes_organicos', 'Solventes Orgânicos'),
        ('metais_pesados', 'Metais Pesados'),
        ('acidos_bases', 'Ácidos e Bases'),
        ('laboratorio_quimico', 'Laboratório Químico'),
        ('farmaceutico', 'Farmacêutico'),
        ('outros_perigosos', 'Outros Perigosos'),
    ]
    
    # Identificação
    identificacao = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Identificação'
    )
    codigo_qr = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código QR'
    )
    
    # Empresa responsável
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='bombonas',
        verbose_name='Empresa'
    )
    
    # Localização
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Latitude'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Longitude'
    )
    endereco_instalacao = models.CharField(
        max_length=300,
        verbose_name='Endereço de Instalação'
    )
    
    # Características
    capacidade = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Capacidade (kg)',
        help_text='Capacidade máxima em quilogramas'
    )
    tipo_residuo = models.CharField(
        max_length=30,
        choices=TIPO_RESIDUO_CHOICES,
        verbose_name='Tipo de Resíduo'
    )
    descricao_residuo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição do Resíduo'
    )
    
    # Status e leituras
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal',
        verbose_name='Status'
    )
    peso_atual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.0,
        verbose_name='Peso Atual (kg)'
    )
    temperatura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.0,
        verbose_name='Temperatura (°C)'
    )
    ultima_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Leitura'
    )
    
    # Controle
    data_instalacao = models.DateField(verbose_name='Data de Instalação')
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Bombona'
        verbose_name_plural = 'Bombonas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identificacao']),
            models.Index(fields=['empresa']),
            models.Index(fields=['status']),
            models.Index(fields=['tipo_residuo']),
        ]
    
    def __str__(self):
        return f"{self.identificacao} - {self.empresa.nome}"
    
    @property
    def percentual_ocupacao(self):
        """Retorna percentual de ocupação da bombona"""
        if self.capacidade > 0:
            return round((float(self.peso_atual) / float(self.capacidade)) * 100, 2)
        return 0.0
    
    @property
    def necessita_coleta(self):
        """Verifica se a bombona necessita coleta"""
        return self.percentual_ocupacao >= 80
    
    @property
    def status_color(self):
        """Retorna cor do status para o mapa"""
        colors = {
            'normal': 'green',
            'quase_cheia': 'yellow',
            'cheia': 'red',
            'manutencao': 'gray',
            'inativa': 'black',
        }
        return colors.get(self.status, 'gray')
    
    def atualizar_status(self):
        """Atualiza status baseado no percentual de ocupação"""
        if not self.is_active:
            self.status = 'inativa'
        elif self.status == 'manutencao':
            pass  # Mantém em manutenção
        elif self.percentual_ocupacao >= 95:
            self.status = 'cheia'
        elif self.percentual_ocupacao >= 80:
            self.status = 'quase_cheia'
        else:
            self.status = 'normal'
        
        self.save(update_fields=['status', 'updated_at'])


class LeituraSensor(models.Model):
    """Modelo para armazenar histórico de leituras dos sensores"""
    
    bombona = models.ForeignKey(
        Bombona,
        on_delete=models.CASCADE,
        related_name='leituras',
        verbose_name='Bombona'
    )
    peso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Peso (kg)'
    )
    temperatura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Temperatura (°C)'
    )
    data_leitura = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Leitura'
    )
    simulado = models.BooleanField(
        default=True,
        verbose_name='Leitura Simulada'
    )
    
    class Meta:
        verbose_name = 'Leitura de Sensor'
        verbose_name_plural = 'Leituras de Sensores'
        ordering = ['-data_leitura']
        indexes = [
            models.Index(fields=['bombona', '-data_leitura']),
        ]
    
    def __str__(self):
        return f"{self.bombona.identificacao} - {self.data_leitura.strftime('%d/%m/%Y %H:%M')}"
