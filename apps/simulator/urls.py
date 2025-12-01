from django.urls import path
from .views import (
    iniciar_simulacao, simular_bombona, resetar_bombona,
    popular_dados_exemplo, status_simulador
)

urlpatterns = [
    path('iniciar/', iniciar_simulacao, name='iniciar-simulacao'),
    path('status/', status_simulador, name='status-simulador'),
    path('bombona/<int:pk>/simular/', simular_bombona, name='simular-bombona'),
    path('bombona/<int:pk>/resetar/', resetar_bombona, name='resetar-bombona'),
    path('popular-dados/', popular_dados_exemplo, name='popular-dados'),
]
