from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from apps.productos.models import Producto
from apps.ventas.models import Venta, DetalleVenta
from decimal import Decimal
import json

def dashboard(request):
    productos_total = Producto.objects.filter(activo=True).count()
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=5, 
        activo=True
    ).count()
    
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    total_ventas_hoy = sum(venta.total for venta in ventas_hoy)
    
    context = {
        'productos_total': productos_total,
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_hoy_count': ventas_hoy.count(),
        'total_ventas_hoy': total_ventas_hoy,
    }
    return render(request, 'dashboard.html', context)

def punto_venta(request):
    productos = Producto.objects.filter(activo=True, stock_actual__gt=0).order_by('nombre')
    context = {
        'productos': productos,
    }
    return render(request, 'punto_venta.html', context)

# API para obtener productos
def api_productos(request):
    productos = Producto.objects.filter(activo=True, stock_actual__gt=0)
    data = []
    for producto in productos:
        data.append({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio_venta': float(producto.precio_venta),
            'stock_actual': producto.stock_actual,
        })
    return JsonResponse({'productos': data})

# API para procesar venta
@csrf_exempt
def api_procesar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productos_venta = data.get('productos', [])
            efectivo_recibido = Decimal(str(data.get('efectivo_recibido', 0)))
            
            if not productos_venta:
                return JsonResponse({'error': 'No hay productos en la venta'}, status=400)
            
            with transaction.atomic():
                # Generar número de venta
                ultimo_numero = Venta.objects.count() + 1
                numero_venta = f"V{ultimo_numero:06d}"
                
                # Calcular total
                total = Decimal('0')
                detalles = []
                
                for item in productos_venta:
                    producto = get_object_or_404(Producto, id=item['producto_id'])
                    cantidad = int(item['cantidad'])
                    precio_unitario = producto.precio_venta
                    subtotal = precio_unitario * cantidad
                    total += subtotal
                    
                    # Verificar stock
                    if producto.stock_actual < cantidad:
                        return JsonResponse({
                            'error': f'Stock insuficiente para {producto.nombre}'
                        }, status=400)
                    
                    detalles.append({
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario,
                        'subtotal': subtotal
                    })
                
                # Crear venta
                cambio = efectivo_recibido - total
                if cambio < 0:
                    return JsonResponse({'error': 'Efectivo insuficiente'}, status=400)
                
                venta = Venta.objects.create(
                    numero_venta=numero_venta,
                    total=total,
                    efectivo_recibido=efectivo_recibido,
                    cambio=cambio
                )
                
                # Crear detalles y actualizar stock
                for detalle in detalles:
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=detalle['producto'],
                        cantidad=detalle['cantidad'],
                        precio_unitario=detalle['precio_unitario'],
                        subtotal=detalle['subtotal']
                    )
                    
                    # Actualizar stock
                    producto = detalle['producto']
                    producto.stock_actual -= detalle['cantidad']
                    producto.save()
                
                return JsonResponse({
                    'success': True,
                    'venta_id': venta.id,
                    'numero_venta': venta.numero_venta,
                    'total': float(venta.total),
                    'cambio': float(venta.cambio)
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)