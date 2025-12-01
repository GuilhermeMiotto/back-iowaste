from rest_framework import serializers
from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer completo para o modelo Empresa"""
    
    endereco_completo = serializers.ReadOnlyField()
    bombonas_count = serializers.SerializerMethodField()
    bombonas_ativas = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'nome', 'cnpj', 'razao_social',
            'endereco', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'cep', 'endereco_completo',
            'telefone', 'email', 'responsavel',
            'inscricao_estadual', 'atividade_principal',
            'bombonas_count', 'bombonas_ativas',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'bombonas_count', 'bombonas_ativas']
    
    def get_bombonas_count(self, obj):
        """Retorna o número total de bombonas da empresa"""
        return obj.bombonas.count()
    
    def get_bombonas_ativas(self, obj):
        """Retorna o número de bombonas ativas da empresa"""
        return obj.bombonas.filter(is_active=True).count()
    
    def validate_cnpj(self, value):
        """Validar formato do CNPJ"""
        if not value:
            raise serializers.ValidationError('CNPJ é obrigatório')
            
        # Remove caracteres especiais
        cnpj_numeros = ''.join(filter(str.isdigit, value))
        
        if len(cnpj_numeros) != 14:
            raise serializers.ValidationError('CNPJ deve conter 14 dígitos')
        
        # Verificar se já existe outra empresa com o mesmo CNPJ
        if self.instance:
            # Atualização - excluir a própria instância da verificação
            if Empresa.objects.filter(cnpj=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Já existe uma empresa com este CNPJ')
        else:
            # Criação - verificar se já existe
            if Empresa.objects.filter(cnpj=value).exists():
                raise serializers.ValidationError('Já existe uma empresa com este CNPJ')
        
        return value
    
    def validate_email(self, value):
        """Validar formato do email"""
        if value and '@' not in value:
            raise serializers.ValidationError('Email deve ter um formato válido')
        return value


class EmpresaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de empresas"""
    
    bombonas_count = serializers.SerializerMethodField()
    endereco_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'nome', 'cnpj', 'razao_social', 'cidade', 
            'estado', 'telefone', 'email', 'responsavel',
            'endereco_completo', 'bombonas_count', 'is_active'
        ]
    
    def get_bombonas_count(self, obj):
        """Retorna o número total de bombonas da empresa"""
        return obj.bombonas.count()


class EmpresaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de empresas"""
    
    class Meta:
        model = Empresa
        fields = [
            'nome', 'cnpj', 'razao_social',
            'endereco', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'cep',
            'telefone', 'email', 'responsavel',
            'inscricao_estadual', 'atividade_principal'
        ]
    
    def validate_cnpj(self, value):
        """Validar CNPJ único"""
        cnpj_numeros = ''.join(filter(str.isdigit, value))
        if len(cnpj_numeros) != 14:
            raise serializers.ValidationError('CNPJ deve conter 14 dígitos')
        if Empresa.objects.filter(cnpj=value).exists():
            raise serializers.ValidationError('Já existe uma empresa com este CNPJ')
        return value
