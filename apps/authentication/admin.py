from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Log


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'tipo_usuario', 'is_active', 'created_at']
    list_filter = ['tipo_usuario', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'cpf_cnpj']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('tipo_usuario', 'telefone', 'cpf_cnpj')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('email', 'tipo_usuario', 'telefone', 'cpf_cnpj')
        }),
    )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_acao', 'descricao', 'ip_address', 'data']
    list_filter = ['tipo_acao', 'data']
    search_fields = ['usuario__email', 'descricao', 'ip_address']
    readonly_fields = ['usuario', 'tipo_acao', 'descricao', 'ip_address', 'user_agent', 'data', 'detalhes']
    ordering = ['-data']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
