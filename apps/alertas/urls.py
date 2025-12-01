from django.urls import path
from .views import (
    AlertaListCreateView, AlertaDetailView,
    resolver_alerta, alertas_estatisticas
)

urlpatterns = [
    path('', AlertaListCreateView.as_view(), name='alerta-list-create'),
    path('<int:pk>/', AlertaDetailView.as_view(), name='alerta-detail'),
    path('<int:pk>/resolver/', resolver_alerta, name='resolver-alerta'),
    path('estatisticas/', alertas_estatisticas, name='alertas-estatisticas'),
]
