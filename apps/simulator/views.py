from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.authentication.permissions import IsOperadorOrAdmin
from .simulator import simulator
from apps.bombonas.models import Bombona


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def iniciar_simulacao(request):
    """Inicia uma simulação manual de todas as bombonas"""
    
    resultado = simulator.simular_todas_bombonas()
    
    return Response({
        'mensagem': 'Simulação executada com sucesso',
        'resultado': resultado
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def simular_bombona(request, pk):
    """Simula leitura para uma bombona específica"""
    
    try:
        bombona = Bombona.objects.get(pk=pk)
    except Bombona.DoesNotExist:
        return Response(
            {'erro': 'Bombona não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    leitura = simulator.simular_leitura_bombona(bombona)
    
    if leitura:
        return Response({
            'mensagem': 'Leitura simulada com sucesso',
            'bombona': bombona.identificacao,
            'peso_atual': float(bombona.peso_atual),
            'temperatura': float(bombona.temperatura),
            'percentual_ocupacao': bombona.percentual_ocupacao,
            'status': bombona.status
        })
    else:
        return Response(
            {'erro': 'Não foi possível simular leitura para esta bombona'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def resetar_bombona(request, pk):
    """Reseta uma bombona (esvazia)"""
    
    try:
        bombona = Bombona.objects.get(pk=pk)
    except Bombona.DoesNotExist:
        return Response(
            {'erro': 'Bombona não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    simulator.resetar_bombona(bombona)
    
    return Response({
        'mensagem': 'Bombona resetada com sucesso',
        'bombona': bombona.identificacao,
        'peso_atual': float(bombona.peso_atual),
        'status': bombona.status
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsOperadorOrAdmin])
def popular_dados_exemplo(request):
    """Popula o banco com dados de exemplo"""
    
    resultado = simulator.popular_dados_exemplo()
    
    return Response({
        'mensagem': resultado
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def status_simulador(request):
    """Retorna status do simulador"""
    
    from apps.bombonas.models import Bombona, LeituraSensor
    from apps.alertas.models import Alerta
    from django.utils import timezone
    from datetime import timedelta
    
    # Leituras nas últimas 24h
    ontem = timezone.now() - timedelta(hours=24)
    leituras_24h = LeituraSensor.objects.filter(
        data_leitura__gte=ontem,
        simulado=True
    ).count()
    
    return Response({
        'bombonas_ativas': Bombona.objects.filter(is_active=True).count(),
        'leituras_24h': leituras_24h,
        'alertas_abertos': Alerta.objects.filter(resolvido=False).count(),
        'status': 'ativo'
    })
