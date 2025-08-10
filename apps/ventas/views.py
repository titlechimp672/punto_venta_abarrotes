from django.shortcuts import render
from .models import Venta, DetalleVenta

def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    context = {
        'ventas': ventas,
    }
    return render(request, 'ventas/lista.html', context)