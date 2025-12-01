from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, RegisterSerializer, 
    LoginSerializer, LogSerializer
)
from .models import Log
from .permissions import IsAdmin, IsAdminOrReadOnly

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View para registro de novos usuários"""
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Criar log
        Log.objects.create(
            usuario=user,
            tipo_acao='create',
            descricao=f'Novo usuário registrado: {user.email}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """View para login de usuários"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Criar log
        Log.objects.create(
            usuario=user,
            tipo_acao='login',
            descricao=f'Usuário realizou login: {user.email}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class LogoutView(APIView):
    """View para logout de usuários"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Criar log
            Log.objects.create(
                usuario=request.user,
                tipo_acao='logout',
                descricao=f'Usuário realizou logout: {request.user.email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )
            
            return Response({
                'message': 'Logout realizado com sucesso.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """View para listar usuários"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['tipo_usuario', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View para detalhes, atualização e exclusão de usuário"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Permitir que usuários vejam apenas seu próprio perfil, exceto admins"""
        pk = self.kwargs.get('pk')
        if pk == 'me' or (not self.request.user.is_admin and int(pk) != self.request.user.id):
            return self.request.user
        return super().get_object()


class LogListView(generics.ListAPIView):
    """View para listar logs"""
    
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filterset_fields = ['usuario', 'tipo_acao']
    search_fields = ['descricao']


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """Retorna informações do usuário autenticado"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
