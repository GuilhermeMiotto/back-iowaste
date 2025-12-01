from django.contrib import admin
from .models import Alerta


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = [
        'bombona', 'tipo', 'nivel', 'descricao',
        'resolvido', 'data_alerta', 'data_resolucao'
    ]
    list_filter = ['tipo', 'nivel', 'resolvido', 'data_alerta']
    search_fields = ['bombona__identificacao', 'descricao']
    readonly_fields = ['data_alerta', 'created_at', 'updated_at']
    ordering = ['-data_alerta']
    
    fieldsets = (
        ('Alerta', {
            'fields': ('bombona', 'tipo', 'nivel', 'descricao', 'data_alerta')
        }),
        ('Resolução', {
            'fields': ('resolvido', 'data_resolucao', 'observacoes_resolucao')
        }),
        ('Controle', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['marcar_como_resolvido']
    
    def marcar_como_resolvido(self, request, queryset):
        from django.utils import timezone
        queryset.update(resolvido=True, data_resolucao=timezone.now())
        self.message_user(request, f'{queryset.count()} alertas marcados como resolvidos.')
    marcar_como_resolvido.short_description = 'Marcar como resolvido'
