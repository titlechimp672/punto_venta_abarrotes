from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('api/<int:producto_id>/', views.api_producto_detalle, name='api_detalle'),
]