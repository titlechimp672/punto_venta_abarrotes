from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio_venta', 'stock_actual', 'necesita_restock', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)
    
    def necesita_restock(self, obj):
        return obj.necesita_restock
    necesita_restock.boolean = True
    necesita_restock.short_description = 'Necesita Restock'