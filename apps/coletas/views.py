from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Coleta
from .serializers import ColetaSerializer, ColetaListSerializer
from apps.authentication.permissions import IsOperadorOrAdmin


class ColetaListCreateView(generics.ListCreateAPIView):
    """View para listar e criar coletas"""
    
    queryset = Coleta.objects.select_related('bombona', 'operador').all()
    permission_classes = [permissions.IsAuthenticated, IsOperadorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'bombona', 'operador']
    search_fields = ['bombona__identificacao', 'destino', 'numero_manifesto']
    ordering_fields = ['data_coleta', 'peso_coletado']
    ordering = ['-data_coleta']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ColetaListSerializer
        return ColetaSerializer
    
    def perform_create(self, serializer):
        # Definir operador como usuário atual se não especificado
        if not serializer.validated_data.get('operador'):
            serializer.save(operador=self.request.user)
        else:
            serializer.save()


class ColetaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View para detalhes, atualização e exclusão de coleta"""
    
    queryset = Coleta.objects.select_related('bombona', 'operador').all()
    serializer_class = ColetaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOperadorOrAdmin]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def coletas_estatisticas(request):
    """Estatísticas de coletas"""
    
    queryset = Coleta.objects.all()
    
    # Filtros por período
    periodo = request.query_params.get('periodo', 'mes')  # mes, semana, ano
    
    stats = {
        'total_coletas': queryset.count(),
        'coletas_pendentes': queryset.filter(status='pendente').count(),
        'coletas_concluidas': queryset.filter(status='concluida').count(),
        'peso_total_coletado': queryset.filter(status='concluida').aggregate(
            total=Sum('peso_coletado')
        )['total'] or 0,
    }
    
    return Response(stats)
