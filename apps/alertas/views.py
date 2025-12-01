from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Alerta
from .serializers import AlertaSerializer, AlertaListSerializer
from apps.authentication.permissions import IsOperadorOrAdmin


class AlertaListCreateView(generics.ListCreateAPIView):
    """View para listar e criar alertas"""
    
    queryset = Alerta.objects.select_related('bombona').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'nivel', 'resolvido', 'bombona']
    search_fields = ['descricao', 'bombona__identificacao']
    ordering_fields = ['data_alerta', 'nivel']
    ordering = ['-data_alerta']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AlertaListSerializer
        return AlertaSerializer


class AlertaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View para detalhes, atualização e exclusão de alerta"""
    
    queryset = Alerta.objects.select_related('bombona').all()
    serializer_class = AlertaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOperadorOrAdmin]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def resolver_alerta(request, pk):
    """Marcar alerta como resolvido"""
    
    try:
        alerta = Alerta.objects.get(pk=pk)
    except Alerta.DoesNotExist:
        return Response(
            {'error': 'Alerta não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if alerta.resolvido:
        return Response(
            {'error': 'Alerta já foi resolvido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    alerta.resolvido = True
    alerta.data_resolucao = timezone.now()
    alerta.observacoes_resolucao = request.data.get('observacoes', '')
    alerta.save()
    
    serializer = AlertaSerializer(alerta)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def alertas_estatisticas(request):
    """Estatísticas de alertas"""
    
    queryset = Alerta.objects.all()
    
    stats = {
        'total_alertas': queryset.count(),
        'alertas_abertos': queryset.filter(resolvido=False).count(),
        'alertas_resolvidos': queryset.filter(resolvido=True).count(),
        'alertas_criticos': queryset.filter(nivel='critico', resolvido=False).count(),
        'alertas_altos': queryset.filter(nivel='alto', resolvido=False).count(),
    }
    
    return Response(stats)
