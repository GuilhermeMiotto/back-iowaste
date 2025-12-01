from rest_framework import serializers
from .models import Bombona, LeituraSensor
from apps.empresas.serializers import EmpresaListSerializer


class BombonaSerializer(serializers.ModelSerializer):
    """Serializer completo para Bombona"""
    
    empresa_detalhes = EmpresaListSerializer(source='empresa', read_only=True)
    percentual_ocupacao = serializers.ReadOnlyField()
    necessita_coleta = serializers.ReadOnlyField()
    status_color = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tipo_residuo_display = serializers.CharField(source='get_tipo_residuo_display', read_only=True)
    
    class Meta:
        model = Bombona
        fields = [
            'id', 'identificacao', 'codigo_qr', 'empresa', 'empresa_detalhes',
            'latitude', 'longitude', 'endereco_instalacao',
            'capacidade', 'tipo_residuo', 'tipo_residuo_display', 'descricao_residuo',
            'status', 'status_display', 'status_color', 'peso_atual', 'temperatura',
            'percentual_ocupacao', 'necessita_coleta', 'ultima_leitura',
            'data_instalacao', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ultima_leitura']
    
    def validate(self, attrs):
        """Validações customizadas"""
        peso_atual = attrs.get('peso_atual', 0)
        capacidade = attrs.get('capacidade')
        
        if peso_atual < 0:
            raise serializers.ValidationError({
                'peso_atual': 'O peso não pode ser negativo.'
            })
        
        if capacidade and peso_atual > capacidade:
            raise serializers.ValidationError({
                'peso_atual': 'O peso atual não pode ser maior que a capacidade.'
            })
        
        return attrs


class BombonaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    percentual_ocupacao = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tipo_residuo_display = serializers.CharField(source='get_tipo_residuo_display', read_only=True)
    status_color = serializers.ReadOnlyField()
    
    class Meta:
        model = Bombona
        fields = [
            'id', 'identificacao', 'empresa_nome', 'status', 'status_display',
            'status_color', 'tipo_residuo', 'tipo_residuo_display',
            'peso_atual', 'capacidade', 'percentual_ocupacao',
            'latitude', 'longitude', 'is_active'
        ]


class BombonaMapSerializer(serializers.ModelSerializer):
    """Serializer otimizado para visualização no mapa"""
    
    percentual_ocupacao = serializers.ReadOnlyField()
    status_color = serializers.ReadOnlyField()
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    
    class Meta:
        model = Bombona
        fields = [
            'id', 'identificacao', 'latitude', 'longitude',
            'status', 'status_color', 'tipo_residuo',
            'peso_atual', 'capacidade', 'percentual_ocupacao',
            'empresa_nome', 'endereco_instalacao'
        ]


class LeituraSensorSerializer(serializers.ModelSerializer):
    """Serializer para leituras de sensores"""
    
    bombona_identificacao = serializers.CharField(source='bombona.identificacao', read_only=True)
    
    class Meta:
        model = LeituraSensor
        fields = [
            'id', 'bombona', 'bombona_identificacao',
            'peso', 'temperatura', 'data_leitura', 'simulado'
        ]
        read_only_fields = ['id', 'data_leitura']


class BombonaEstatsticasSerializer(serializers.Serializer):
    """Serializer para estatísticas das bombonas"""
    
    total_bombonas = serializers.IntegerField()
    bombonas_ativas = serializers.IntegerField()
    bombonas_normais = serializers.IntegerField()
    bombonas_quase_cheias = serializers.IntegerField()
    bombonas_cheias = serializers.IntegerField()
    bombonas_manutencao = serializers.IntegerField()
    peso_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentual_medio_ocupacao = serializers.DecimalField(max_digits=5, decimal_places=2)
