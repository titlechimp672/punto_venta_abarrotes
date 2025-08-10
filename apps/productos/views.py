from django.shortcuts import render
from django.http import JsonResponse
from .models import Producto

def lista_productos(request):
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    context = {
        'productos': productos,
    }
    return render(request, 'productos/lista.html', context)

def api_producto_detalle(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
        data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio_venta': float(producto.precio_venta),
            'stock_actual': producto.stock_actual,
            'necesita_restock': producto.necesita_restock,
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)