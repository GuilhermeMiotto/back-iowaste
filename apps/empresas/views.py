from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Empresa
from .serializers import EmpresaSerializer, EmpresaListSerializer, EmpresaCreateSerializer
from apps.authentication.permissions import IsAdminOrReadOnly


class EmpresaListCreateView(generics.ListCreateAPIView):
    """View para listar e criar empresas"""
    
    queryset = Empresa.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cidade', 'is_active']
    search_fields = ['nome', 'cnpj', 'razao_social', 'cidade', 'responsavel']
    ordering_fields = ['nome', 'created_at', 'cidade']
    ordering = ['nome']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmpresaListSerializer
        elif self.request.method == 'POST':
            return EmpresaCreateSerializer
        return EmpresaSerializer
    
    def get_queryset(self):
        """Personalizar queryset com anotações"""
        queryset = super().get_queryset()
        
        # Adicionar contagem de bombonas
        queryset = queryset.annotate(
            total_bombonas=Count('bombonas'),
            bombonas_ativas=Count('bombonas', filter=Q(bombonas__is_active=True))
        )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Customizar resposta da listagem com estatísticas"""
        response = super().list(request, *args, **kwargs)
        
        # Adicionar estatísticas gerais
        total_empresas = self.get_queryset().count()
        empresas_ativas = self.get_queryset().filter(is_active=True).count()
        
        response.data = {
            'count': response.data.get('count', total_empresas),
            'results': response.data.get('results', response.data),
            'statistics': {
                'total_empresas': total_empresas,
                'empresas_ativas': empresas_ativas,
                'empresas_inativas': total_empresas - empresas_ativas,
            }
        }
        
        return response


class EmpresaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View para detalhes, atualização e exclusão de empresa"""
    
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Adicionar prefetch de bombonas relacionadas"""
        return super().get_queryset().prefetch_related('bombonas')
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - desativar ao invés de excluir"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(
            {'message': 'Empresa desativada com sucesso'}, 
            status=status.HTTP_200_OK
        )


class EmpresaStatsView(generics.GenericAPIView):
    """View para estatísticas detalhadas das empresas"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Retornar estatísticas das empresas"""
        from django.db.models import Avg, Sum
        from apps.bombonas.models import Bombona
        from apps.coletas.models import Coleta
        
        # Estatísticas básicas
        total_empresas = Empresa.objects.count()
        empresas_ativas = Empresa.objects.filter(is_active=True).count()
        
        # Estatísticas por estado
        empresas_por_estado = list(
            Empresa.objects.values('estado')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # Top empresas por número de bombonas
        top_empresas_bombonas = list(
            Empresa.objects.annotate(
                bombonas_count=Count('bombonas')
            ).filter(bombonas_count__gt=0)
            .order_by('-bombonas_count')[:5]
            .values('nome', 'bombonas_count')
        )
        
        # Empresas com mais coletas
        top_empresas_coletas = list(
            Empresa.objects.annotate(
                coletas_count=Count('bombonas__coletas')
            ).filter(coletas_count__gt=0)
            .order_by('-coletas_count')[:5]
            .values('nome', 'coletas_count')
        )
        
        return Response({
            'geral': {
                'total_empresas': total_empresas,
                'empresas_ativas': empresas_ativas,
                'empresas_inativas': total_empresas - empresas_ativas,
                'percentual_ativas': round((empresas_ativas / total_empresas * 100), 2) if total_empresas > 0 else 0
            },
            'por_estado': empresas_por_estado,
            'top_bombonas': top_empresas_bombonas,
            'top_coletas': top_empresas_coletas
        })
