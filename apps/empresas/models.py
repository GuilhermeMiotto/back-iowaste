from django.db import models
from django.core.validators import RegexValidator


class Empresa(models.Model):
    """Modelo de Empresa Geradora de Resíduos"""
    
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                message='CNPJ deve estar no formato: 00.000.000/0000-00'
            )
        ],
        verbose_name='CNPJ'
    )
    razao_social = models.CharField(max_length=200, verbose_name='Razão Social')
    
    # Endereço
    endereco = models.CharField(max_length=300, verbose_name='Endereço')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    
    # Contato
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(verbose_name='E-mail')
    responsavel = models.CharField(max_length=150, verbose_name='Responsável')
    
    # Informações adicionais
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Inscrição Estadual'
    )
    atividade_principal = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Atividade Principal'
    )
    
    # Controle
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cnpj']),
        ]
    
    def __str__(self):
        return f"{self.nome} - {self.cnpj}"
    
    @property
    def endereco_completo(self):
        """Retorna endereço completo formatado"""
        complemento = f", {self.complemento}" if self.complemento else ""
        return (
            f"{self.endereco}, {self.numero}{complemento} - "
            f"{self.bairro}, {self.cidade}/{self.estado} - "
            f"CEP: {self.cep}"
        )
