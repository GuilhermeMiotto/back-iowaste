from rest_framework import serializers
from .models import Coleta
from apps.bombonas.serializers import BombonaListSerializer
from apps.authentication.serializers import UserSerializer


class ColetaSerializer(serializers.ModelSerializer):
    """Serializer completo para Coleta"""
    
    bombona_detalhes = BombonaListSerializer(source='bombona', read_only=True)
    operador_nome = serializers.CharField(source='operador.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Coleta
        fields = [
            'id', 'bombona', 'bombona_detalhes', 'operador', 'operador_nome',
            'data_coleta', 'peso_coletado', 'destino', 'empresa_destino',
            'status', 'status_display', 'observacoes', 'numero_manifesto',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validações"""
        peso_coletado = attrs.get('peso_coletado')
        bombona = attrs.get('bombona')
        
        if peso_coletado <= 0:
            raise serializers.ValidationError({
                'peso_coletado': 'O peso coletado deve ser maior que zero.'
            })
        
        if bombona and peso_coletado > bombona.peso_atual:
            raise serializers.ValidationError({
                'peso_coletado': f'O peso coletado não pode ser maior que o peso atual da bombona ({bombona.peso_atual} kg).'
            })
        
        return attrs


class ColetaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    
    bombona_identificacao = serializers.CharField(source='bombona.identificacao', read_only=True)
    operador_nome = serializers.CharField(source='operador.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Coleta
        fields = [
            'id', 'bombona_identificacao', 'operador_nome',
            'data_coleta', 'peso_coletado', 'destino',
            'status', 'status_display'
        ]
