from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'cnpj', 'cidade', 'estado',
        'telefone', 'email', 'is_active', 'created_at'
    ]
    list_filter = ['estado', 'cidade', 'is_active', 'created_at']
    search_fields = ['nome', 'cnpj', 'razao_social', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cnpj', 'razao_social', 'inscricao_estadual', 'atividade_principal')
        }),
        ('Endereço', {
            'fields': (
                'endereco', 'numero', 'complemento',
                'bairro', 'cidade', 'estado', 'cep'
            )
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'responsavel')
        }),
        ('Controle', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
