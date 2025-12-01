from django.urls import path
from .views import (
    BombonaListCreateView, BombonaDetailView,
    bombonas_mapa, bombonas_estatisticas,
    atualizar_status_bombona, LeituraSensorListView,
    historico_bombona
)

urlpatterns = [
    path('', BombonaListCreateView.as_view(), name='bombona-list-create'),
    path('<int:pk>/', BombonaDetailView.as_view(), name='bombona-detail'),
    path('mapa/', bombonas_mapa, name='bombonas-mapa'),
    path('estatisticas/', bombonas_estatisticas, name='bombonas-estatisticas'),
    path('<int:pk>/atualizar-status/', atualizar_status_bombona, name='atualizar-status-bombona'),
    path('<int:pk>/historico/', historico_bombona, name='historico-bombona'),
    path('leituras/', LeituraSensorListView.as_view(), name='leituras-sensores'),
]
