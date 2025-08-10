"""
URL configuration for punto_venta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('pos/', views.punto_venta, name='punto_venta'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/procesar-venta/', views.api_procesar_venta, name='api_procesar_venta'),
    path('productos/', include('apps.productos.urls')),
    path('ventas/', include('apps.ventas.urls')),
]