from django.urls import path
from .views import EmpresaListCreateView, EmpresaDetailView, EmpresaStatsView

urlpatterns = [
    path('', EmpresaListCreateView.as_view(), name='empresa-list-create'),
    path('<int:pk>/', EmpresaDetailView.as_view(), name='empresa-detail'),
    path('stats/', EmpresaStatsView.as_view(), name='empresa-stats'),
]
