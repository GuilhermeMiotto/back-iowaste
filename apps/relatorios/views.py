from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from apps.bombonas.models import Bombona
from apps.coletas.models import Coleta
from apps.alertas.models import Alerta
from apps.empresas.models import Empresa
import calendar


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def relatorio_mensal(request):
    """Relatório mensal de resíduos"""
    
    # Obter mês e ano dos parâmetros ou usar mês atual
    ano = int(request.query_params.get('ano', datetime.now().year))
    mes = int(request.query_params.get('mes', datetime.now().month))
    
    # Filtrar coletas do mês
    coletas = Coleta.objects.filter(
        data_coleta__year=ano,
        data_coleta__month=mes,
        status='concluida'
    )
    
    # Estatísticas
    total_coletado = coletas.aggregate(total=Sum('peso_coletado'))['total'] or 0
    total_coletas = coletas.count()
    
    # Por tipo de resíduo
    por_tipo = {}
    for coleta in coletas.select_related('bombona'):
        tipo = coleta.bombona.tipo_residuo
        if tipo not in por_tipo:
            por_tipo[tipo] = {'peso': 0, 'coletas': 0}
        por_tipo[tipo]['peso'] += float(coleta.peso_coletado)
        por_tipo[tipo]['coletas'] += 1
    
    # Alertas do mês
    alertas_mes = Alerta.objects.filter(
        data_alerta__year=ano,
        data_alerta__month=mes
    ).count()
    
    return Response({
        'periodo': f'{mes:02d}/{ano}',
        'total_peso_coletado': float(total_coletado),
        'total_coletas': total_coletas,
        'por_tipo_residuo': por_tipo,
        'alertas_gerados': alertas_mes,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def relatorio_por_tipo_residuo(request):
    """Relatório por tipo de resíduo"""
    
    bombonas = Bombona.objects.filter(is_active=True)
    
    relatorio = {}
    for tipo, nome in Bombona.TIPO_RESIDUO_CHOICES:
        bombonas_tipo = bombonas.filter(tipo_residuo=tipo)
        
        # Coletas do tipo
        coletas = Coleta.objects.filter(
            bombona__tipo_residuo=tipo,
            status='concluida'
        )
        
        relatorio[tipo] = {
            'nome': nome,
            'total_bombonas': bombonas_tipo.count(),
            'peso_armazenado': float(bombonas_tipo.aggregate(total=Sum('peso_atual'))['total'] or 0),
            'peso_coletado_total': float(coletas.aggregate(total=Sum('peso_coletado'))['total'] or 0),
            'total_coletas': coletas.count(),
        }
    
    return Response(relatorio)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def relatorio_por_empresa(request):
    """Relatório por empresa"""
    
    from apps.empresas.models import Empresa
    
    empresas = Empresa.objects.filter(is_active=True)
    relatorio = []
    
    for empresa in empresas:
        bombonas = Bombona.objects.filter(empresa=empresa, is_active=True)
        coletas = Coleta.objects.filter(bombona__empresa=empresa, status='concluida')
        alertas = Alerta.objects.filter(bombona__empresa=empresa)
        
        relatorio.append({
            'empresa_id': empresa.id,
            'empresa_nome': empresa.nome,
            'empresa_cnpj': empresa.cnpj,
            'total_bombonas': bombonas.count(),
            'peso_armazenado': float(bombonas.aggregate(total=Sum('peso_atual'))['total'] or 0),
            'total_coletas': coletas.count(),
            'peso_total_coletado': float(coletas.aggregate(total=Sum('peso_coletado'))['total'] or 0),
            'total_alertas': alertas.count(),
            'alertas_abertos': alertas.filter(resolvido=False).count(),
        })
    
    return Response(relatorio)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def relatorio_evolucao_coletas(request):
    """Relatório de evolução de coletas ao longo do tempo"""
    
    # Período (últimos 12 meses por padrão)
    meses = int(request.query_params.get('meses', 12))
    data_inicial = datetime.now() - timedelta(days=30 * meses)
    
    coletas = Coleta.objects.filter(
        data_coleta__gte=data_inicial,
        status='concluida'
    ).annotate(
        mes=TruncMonth('data_coleta')
    ).values('mes').annotate(
        total_coletas=Count('id'),
        peso_total=Sum('peso_coletado')
    ).order_by('mes')
    
    evolucao = []
    for item in coletas:
        evolucao.append({
            'mes': item['mes'].strftime('%m/%Y'),
            'total_coletas': item['total_coletas'],
            'peso_total': float(item['peso_total'] or 0),
        })
    
    return Response(evolucao)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_kpis(request):
    """KPIs principais do dashboard"""
    
    # Bombonas
    bombonas_ativas = Bombona.objects.filter(is_active=True)
    total_bombonas = bombonas_ativas.count()
    bombonas_cheias = bombonas_ativas.filter(status='cheia').count()
    bombonas_quase_cheias = bombonas_ativas.filter(status='quase_cheia').count()
    peso_total_armazenado = bombonas_ativas.aggregate(total=Sum('peso_atual'))['total'] or 0
    
    # Coletas
    coletas_mes_atual = Coleta.objects.filter(
        data_coleta__year=datetime.now().year,
        data_coleta__month=datetime.now().month
    )
    coletas_pendentes = Coleta.objects.filter(status='pendente').count()
    coletas_concluidas_mes = coletas_mes_atual.filter(status='concluida').count()
    peso_coletado_mes = coletas_mes_atual.filter(status='concluida').aggregate(
        total=Sum('peso_coletado')
    )['total'] or 0
    
    # Alertas
    alertas_abertos = Alerta.objects.filter(resolvido=False).count()
    alertas_criticos = Alerta.objects.filter(nivel='critico', resolvido=False).count()
    alertas_mes = Alerta.objects.filter(
        data_alerta__year=datetime.now().year,
        data_alerta__month=datetime.now().month
    ).count()
    
    return Response({
        'bombonas': {
            'total': total_bombonas,
            'cheias': bombonas_cheias,
            'quase_cheias': bombonas_quase_cheias,
            'necessitam_coleta': bombonas_cheias + bombonas_quase_cheias,
            'peso_total_armazenado': float(peso_total_armazenado),
        },
        'coletas': {
            'pendentes': coletas_pendentes,
            'concluidas_mes': coletas_concluidas_mes,
            'peso_coletado_mes': float(peso_coletado_mes),
        },
        'alertas': {
            'abertos': alertas_abertos,
            'criticos': alertas_criticos,
            'gerados_mes': alertas_mes,
        },
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_graficos(request):
    """Dados para gráficos do dashboard"""
    
    # Período dos últimos 12 meses
    hoje = datetime.now()
    doze_meses_atras = hoje - timedelta(days=365)
    
    # Evolução mensal de coletas
    coletas_mensais = Coleta.objects.filter(
        data_coleta__gte=doze_meses_atras,
        status='concluida'
    ).extra(
        select={'mes': 'EXTRACT(month FROM data_coleta)', 'ano': 'EXTRACT(year FROM data_coleta)'}
    ).values('mes', 'ano').annotate(
        total_coletas=Count('id'),
        peso_total=Sum('peso_coletado')
    ).order_by('ano', 'mes')
    
    # Formatar dados para gráfico
    evolucao_mensal = []
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for item in coletas_mensais:
        mes_nome = meses_nomes[int(item['mes']) - 1]
        evolucao_mensal.append({
            'mes': f"{mes_nome}/{int(item['ano'])}",
            'coletas': item['total_coletas'],
            'peso': float(item['peso_total'] or 0)
        })
    
    # Distribuição por tipo de resíduo
    tipos_residuo = {}
    bombonas = Bombona.objects.filter(is_active=True).values('tipo_residuo').annotate(
        quantidade=Count('id'),
        peso_atual=Sum('peso_atual')
    )
    
    for item in bombonas:
        tipo = item['tipo_residuo']
        tipos_residuo[tipo] = {
            'bombonas': item['quantidade'],
            'peso_total': float(item['peso_atual'] or 0)
        }
    
    # Status das bombonas
    status_bombonas = {}
    for status, nome in Bombona.STATUS_CHOICES:
        count = Bombona.objects.filter(status=status, is_active=True).count()
        if count > 0:
            status_bombonas[nome] = count
    
    # Empresas mais ativas (por número de coletas)
    empresas_ativas = []
    empresas_data = Empresa.objects.annotate(
        total_coletas=Count('bombonas__coletas', filter=Q(bombonas__coletas__status='concluida'))
    ).filter(total_coletas__gt=0).order_by('-total_coletas')[:5]
    
    for empresa in empresas_data:
        empresas_ativas.append({
            'nome': empresa.nome,
            'coletas': empresa.total_coletas
        })
    
    # Alertas por tipo
    alertas_por_tipo = {}
    alertas_data = Alerta.objects.filter(resolvido=False).values('tipo').annotate(
        quantidade=Count('id')
    )
    
    for item in alertas_data:
        tipo_display = dict(Alerta.TIPO_CHOICES).get(item['tipo'], item['tipo'])
        alertas_por_tipo[tipo_display] = item['quantidade']
    
    return Response({
        'evolucao_mensal': evolucao_mensal,
        'tipos_residuo': tipos_residuo,
        'status_bombonas': status_bombonas,
        'empresas_ativas': empresas_ativas,
        'alertas_por_tipo': alertas_por_tipo
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def relatorio_exportacao(request):
    """Dados para exportação em PDF/Excel"""
    
    formato = request.query_params.get('formato', 'json')  # json, pdf, excel
    periodo = int(request.query_params.get('periodo', 30))  # dias
    
    data_inicial = datetime.now() - timedelta(days=periodo)
    
    # Coletas no período
    coletas = Coleta.objects.filter(
        data_coleta__gte=data_inicial,
        status='concluida'
    ).select_related('bombona', 'bombona__empresa').order_by('-data_coleta')
    
    dados_coletas = []
    for coleta in coletas:
        dados_coletas.append({
            'data': coleta.data_coleta.strftime('%d/%m/%Y %H:%M'),
            'bombona': coleta.bombona.identificacao,
            'empresa': coleta.bombona.empresa.nome,
            'tipo_residuo': coleta.bombona.get_tipo_residuo_display(),
            'peso_coletado': float(coleta.peso_coletado),
            'responsavel': coleta.responsavel_coleta
        })
    
    # Resumo do período
    total_peso = sum(c['peso_coletado'] for c in dados_coletas)
    total_coletas = len(dados_coletas)
    
    # Bombonas por status
    bombonas_resumo = {}
    for status, nome in Bombona.STATUS_CHOICES:
        count = Bombona.objects.filter(status=status, is_active=True).count()
        bombonas_resumo[nome] = count
    
    return Response({
        'periodo': {
            'data_inicial': data_inicial.strftime('%d/%m/%Y'),
            'data_final': datetime.now().strftime('%d/%m/%Y'),
            'dias': periodo
        },
        'resumo': {
            'total_coletas': total_coletas,
            'total_peso': total_peso,
            'media_por_coleta': round(total_peso / total_coletas, 2) if total_coletas > 0 else 0
        },
        'coletas': dados_coletas,
        'bombonas_status': bombonas_resumo,
        'formato_solicitado': formato
    })
