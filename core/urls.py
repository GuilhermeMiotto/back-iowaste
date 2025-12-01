"""
URL configuration for IoWaste project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="IoWaste API",
        default_version='v1',
        description="API para Sistema Inteligente de Gestão e Rastreamento de Resíduos",
        terms_of_service="https://www.iowaste.com/terms/",
        contact=openapi.Contact(email="contato@iowaste.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Routes
    path('api/auth/', include('apps.authentication.urls')),
    path('api/empresas/', include('apps.empresas.urls')),
    path('api/bombonas/', include('apps.bombonas.urls')),
    path('api/coletas/', include('apps.coletas.urls')),
    path('api/alertas/', include('apps.alertas.urls')),
    path('api/relatorios/', include('apps.relatorios.urls')),
    path('api/simulator/', include('apps.simulator.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
