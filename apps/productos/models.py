from django.db import models

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de compra")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de venta")
    stock_actual = models.IntegerField(default=0, verbose_name="Stock actual")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock mínimo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def necesita_restock(self):
        return self.stock_actual <= self.stock_minimo