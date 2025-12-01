from django.urls import path
from .views import (
    relatorio_mensal, relatorio_por_tipo_residuo,
    relatorio_por_empresa, relatorio_evolucao_coletas,
    dashboard_kpis, dashboard_graficos, relatorio_exportacao
)

urlpatterns = [
    path('mensal/', relatorio_mensal, name='relatorio-mensal'),
    path('por-tipo/', relatorio_por_tipo_residuo, name='relatorio-por-tipo'),
    path('por-empresa/', relatorio_por_empresa, name='relatorio-por-empresa'),
    path('evolucao-coletas/', relatorio_evolucao_coletas, name='relatorio-evolucao'),
    path('dashboard-kpis/', dashboard_kpis, name='dashboard-kpis'),
    path('dashboard-graficos/', dashboard_graficos, name='dashboard-graficos'),
    path('exportacao/', relatorio_exportacao, name='relatorio-exportacao'),
]
