from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Modelo customizado de Usuário"""
    
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
        ('empresa', 'Empresa'),
        ('fiscal', 'Fiscal'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='operador',
        verbose_name='Tipo de Usuário'
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True, verbose_name='CPF/CNPJ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_admin(self):
        return self.tipo_usuario == 'admin'
    
    @property
    def is_operador(self):
        return self.tipo_usuario == 'operador'
    
    @property
    def is_empresa(self):
        return self.tipo_usuario == 'empresa'
    
    @property
    def is_fiscal(self):
        return self.tipo_usuario == 'fiscal'


class Log(models.Model):
    """Modelo de Log de Auditoria"""
    
    TIPO_ACAO_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access', 'Acesso'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs',
        verbose_name='Usuário'
    )
    tipo_acao = models.CharField(
        max_length=20,
        choices=TIPO_ACAO_CHOICES,
        verbose_name='Tipo de Ação'
    )
    descricao = models.TextField(verbose_name='Descrição')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    data = models.DateTimeField(auto_now_add=True, verbose_name='Data')
    detalhes = models.JSONField(null=True, blank=True, verbose_name='Detalhes')
    
    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        ordering = ['-data']
        indexes = [
            models.Index(fields=['-data']),
            models.Index(fields=['usuario']),
        ]
    
    def __str__(self):
        return f"{self.usuario} - {self.tipo_acao} - {self.data.strftime('%d/%m/%Y %H:%M')}"
