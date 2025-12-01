from django.urls import path
from .views import ColetaListCreateView, ColetaDetailView, coletas_estatisticas

urlpatterns = [
    path('', ColetaListCreateView.as_view(), name='coleta-list-create'),
    path('<int:pk>/', ColetaDetailView.as_view(), name='coleta-detail'),
    path('estatisticas/', coletas_estatisticas, name='coletas-estatisticas'),
]
