"""
URL configuration for Rifa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from App1 import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.lista_rifas, name='lista_rifas'),
    path('rifa/<int:rifa_id>/', views.detalle_rifa, name='detalle_rifa'),
    path('rifa/<int:rifa_id>/comprar/', views.compra_numero, name='compra_numero'),
    path('rifa/<int:rifa_id>/formulario/', views.formulario_compra, name='formulario'),
    path('rifas_finalizadas/', views.mostrar_rifas_finalizadas, name='mostrar_rifas_finalizadas'),
    path('ganadores/<int:rifa_id>/', views.mostrar_ganadores_por_rifa, name='ganadores_por_rifa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)