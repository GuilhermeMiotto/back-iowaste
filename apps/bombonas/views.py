from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Bombona, LeituraSensor
from .serializers import (
    BombonaSerializer, BombonaListSerializer, BombonaMapSerializer,
    LeituraSensorSerializer, BombonaEstatsticasSerializer
)
from apps.authentication.permissions import IsAdminOrReadOnly, IsOperadorOrAdmin


class BombonaListCreateView(generics.ListCreateAPIView):
    """View para listar e criar bombonas"""
    
    queryset = Bombona.objects.select_related('empresa').all()
    permission_classes = [permissions.IsAuthenticated, IsOperadorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo_residuo', 'empresa', 'is_active']
    search_fields = ['identificacao', 'endereco_instalacao', 'empresa__nome']
    ordering_fields = ['created_at', 'peso_atual', 'capacidade', 'percentual_ocupacao']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BombonaListSerializer
        return BombonaSerializer


class BombonaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View para detalhes, atualização e exclusão de bombona"""
    
    queryset = Bombona.objects.select_related('empresa').all()
    serializer_class = BombonaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOperadorOrAdmin]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def bombonas_mapa(request):
    """Endpoint otimizado para exibição no mapa"""
    
    queryset = Bombona.objects.filter(is_active=True).select_related('empresa')
    
    # Filtros opcionais
    status_filter = request.query_params.get('status')
    tipo_filter = request.query_params.get('tipo_residuo')
    empresa_filter = request.query_params.get('empresa')
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if tipo_filter:
        queryset = queryset.filter(tipo_residuo=tipo_filter)
    if empresa_filter:
        queryset = queryset.filter(empresa_id=empresa_filter)
    
    serializer = BombonaMapSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def bombonas_estatisticas(request):
    """Endpoint para estatísticas gerais das bombonas"""
    
    queryset = Bombona.objects.all()
    
    # Filtros por empresa (se não for admin)
    if not request.user.is_admin and hasattr(request.user, 'empresa'):
        queryset = queryset.filter(empresa=request.user.empresa)
    
    stats = {
        'total_bombonas': queryset.count(),
        'bombonas_ativas': queryset.filter(is_active=True).count(),
        'bombonas_normais': queryset.filter(status='normal').count(),
        'bombonas_quase_cheias': queryset.filter(status='quase_cheia').count(),
        'bombonas_cheias': queryset.filter(status='cheia').count(),
        'bombonas_manutencao': queryset.filter(status='manutencao').count(),
        'peso_total': queryset.aggregate(total=Sum('peso_atual'))['total'] or 0,
        'percentual_medio_ocupacao': 0,
    }
    
    # Calcular percentual médio
    bombonas_ativas = queryset.filter(is_active=True, capacidade__gt=0)
    if bombonas_ativas.exists():
        total_percentual = sum([b.percentual_ocupacao for b in bombonas_ativas])
        stats['percentual_medio_ocupacao'] = round(total_percentual / bombonas_ativas.count(), 2)
    
    serializer = BombonaEstatsticasSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def atualizar_status_bombona(request, pk):
    """Endpoint para atualizar manualmente o status de uma bombona"""
    
    try:
        bombona = Bombona.objects.get(pk=pk)
    except Bombona.DoesNotExist:
        return Response(
            {'error': 'Bombona não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    novo_status = request.data.get('status')
    
    if novo_status not in dict(Bombona.STATUS_CHOICES):
        return Response(
            {'error': 'Status inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    bombona.status = novo_status
    bombona.save()
    
    serializer = BombonaSerializer(bombona)
    return Response(serializer.data)


class LeituraSensorListView(generics.ListAPIView):
    """View para listar leituras de sensores"""
    
    serializer_class = LeituraSensorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bombona', 'simulado']
    ordering = ['-data_leitura']
    
    def get_queryset(self):
        queryset = LeituraSensor.objects.select_related('bombona').all()
        
        # Filtrar por bombona específica
        bombona_id = self.request.query_params.get('bombona_id')
        if bombona_id:
            queryset = queryset.filter(bombona_id=bombona_id)
        
        # Filtrar últimas N leituras
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def historico_bombona(request, pk):
    """Histórico completo de uma bombona"""
    
    try:
        bombona = Bombona.objects.get(pk=pk)
    except Bombona.DoesNotExist:
        return Response(
            {'error': 'Bombona não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Leituras recentes
    leituras = LeituraSensor.objects.filter(bombona=bombona).order_by('-data_leitura')[:50]
    
    # Coletas realizadas
    from apps.coletas.models import Coleta
    coletas = Coleta.objects.filter(bombona=bombona).order_by('-data_coleta')[:20]
    
    # Alertas relacionados
    from apps.alertas.models import Alerta
    alertas = Alerta.objects.filter(bombona=bombona).order_by('-data_alerta')[:20]
    
    return Response({
        'bombona': BombonaSerializer(bombona).data,
        'leituras': LeituraSensorSerializer(leituras, many=True).data,
        'total_leituras': leituras.count(),
        'total_coletas': coletas.count(),
        'total_alertas': alertas.count(),
    })
