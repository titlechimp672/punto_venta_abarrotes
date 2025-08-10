from django.shortcuts import render
from apps.productos.models import Producto
from apps.ventas.models import Venta
from django.utils import timezone

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