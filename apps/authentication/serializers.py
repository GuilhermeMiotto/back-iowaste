from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Log


class UserSerializer(serializers.ModelSerializer):
    """Serializer para o modelo User"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tipo_usuario', 'telefone', 'cpf_cnpj', 'is_active',
            'created_at', 'updated_at', 'password'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Criar usuário com senha criptografada"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Atualizar usuário"""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de novo usuário"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'tipo_usuario', 'telefone', 'cpf_cnpj'
        ]
    
    def validate(self, attrs):
        """Validar senhas"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': 'As senhas não coincidem.'
            })
        return attrs
    
    def create(self, validated_data):
        """Criar novo usuário"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validar credenciais"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciais inválidas.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Conta de usuário desativada.',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'É necessário informar email e senha.',
                code='authorization'
            )
        
        attrs['user'] = user
        return attrs


class LogSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Log"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Log
        fields = [
            'id', 'usuario', 'usuario_nome', 'tipo_acao',
            'descricao', 'ip_address', 'user_agent', 'data', 'detalhes'
        ]
        read_only_fields = ['id', 'data']
