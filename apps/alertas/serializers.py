from rest_framework import serializers
from .models import Alerta


class AlertaSerializer(serializers.ModelSerializer):
    """Serializer completo para Alerta"""
    
    bombona_identificacao = serializers.CharField(source='bombona.identificacao', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    nivel_display = serializers.CharField(source='get_nivel_display', read_only=True)
    nivel_color = serializers.ReadOnlyField()
    
    class Meta:
        model = Alerta
        fields = [
            'id', 'bombona', 'bombona_identificacao',
            'tipo', 'tipo_display', 'nivel', 'nivel_display', 'nivel_color',
            'descricao', 'resolvido', 'data_resolucao', 'observacoes_resolucao',
            'data_alerta', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'data_alerta', 'created_at', 'updated_at']


class AlertaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    
    bombona_identificacao = serializers.CharField(source='bombona.identificacao', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    nivel_display = serializers.CharField(source='get_nivel_display', read_only=True)
    nivel_color = serializers.ReadOnlyField()
    
    class Meta:
        model = Alerta
        fields = [
            'id', 'bombona_identificacao', 'tipo', 'tipo_display',
            'nivel', 'nivel_display', 'nivel_color',
            'descricao', 'resolvido', 'data_alerta'
        ]
