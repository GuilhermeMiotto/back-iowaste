from django.contrib import admin
from .models import Bombona, LeituraSensor


@admin.register(Bombona)
class BombonaAdmin(admin.ModelAdmin):
    list_display = [
        'identificacao', 'empresa', 'tipo_residuo', 'status',
        'peso_atual', 'capacidade', 'percentual_ocupacao',
        'is_active', 'created_at'
    ]
    list_filter = ['status', 'tipo_residuo', 'is_active', 'empresa', 'created_at']
    search_fields = ['identificacao', 'codigo_qr', 'endereco_instalacao', 'empresa__nome']
    readonly_fields = ['created_at', 'updated_at', 'ultima_leitura', 'percentual_ocupacao']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('identificacao', 'codigo_qr', 'empresa')
        }),
        ('Localização', {
            'fields': ('latitude', 'longitude', 'endereco_instalacao')
        }),
        ('Características', {
            'fields': (
                'capacidade', 'tipo_residuo', 'descricao_residuo',
                'data_instalacao'
            )
        }),
        ('Status e Leituras', {
            'fields': (
                'status', 'peso_atual', 'temperatura',
                'percentual_ocupacao', 'ultima_leitura'
            )
        }),
        ('Controle', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['atualizar_status', 'ativar_bombonas', 'desativar_bombonas']
    
    def atualizar_status(self, request, queryset):
        for bombona in queryset:
            bombona.atualizar_status()
        self.message_user(request, f'{queryset.count()} bombonas atualizadas.')
    atualizar_status.short_description = 'Atualizar status das bombonas selecionadas'
    
    def ativar_bombonas(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} bombonas ativadas.')
    ativar_bombonas.short_description = 'Ativar bombonas selecionadas'
    
    def desativar_bombonas(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} bombonas desativadas.')
    desativar_bombonas.short_description = 'Desativar bombonas selecionadas'


@admin.register(LeituraSensor)
class LeituraSensorAdmin(admin.ModelAdmin):
    list_display = ['bombona', 'peso', 'temperatura', 'data_leitura', 'simulado']
    list_filter = ['simulado', 'data_leitura', 'bombona']
    search_fields = ['bombona__identificacao']
    readonly_fields = ['data_leitura']
    ordering = ['-data_leitura']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
