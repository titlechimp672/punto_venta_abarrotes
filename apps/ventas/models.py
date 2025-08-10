from django.db import models
from apps.productos.models import Producto

class Venta(models.Model):
    numero_venta = models.CharField(max_length=20, unique=True, verbose_name="Número de venta")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")
    efectivo_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Efectivo recibido")
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cambio")
    sincronizado = models.BooleanField(default=False, verbose_name="Sincronizado")
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Venta {self.numero_venta} - ${self.total}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    
    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"
        
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"