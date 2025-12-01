from django.contrib import admin
from .models import Coleta


@admin.register(Coleta)
class ColetaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'bombona', 'operador', 'data_coleta',
        'peso_coletado', 'destino', 'status', 'created_at'
    ]
    list_filter = ['status', 'data_coleta', 'operador']
    search_fields = ['bombona__identificacao', 'destino', 'numero_manifesto']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-data_coleta']
    
    fieldsets = (
        ('Coleta', {
            'fields': ('bombona', 'operador', 'data_coleta', 'peso_coletado')
        }),
        ('Destino', {
            'fields': ('destino', 'empresa_destino', 'numero_manifesto')
        }),
        ('Status', {
            'fields': ('status', 'observacoes')
        }),
        ('Controle', {
            'fields': ('created_at', 'updated_at')
        }),
    )
