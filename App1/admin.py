from django.contrib import admin
from .models import Rifa, Premio, Numero, Cliente, Compra, Ganador
# Register your models here.



class NumeroInline(admin.TabularInline):  # O usa `StackedInline` para un diseño diferente
    model = Numero
    extra = 0  # No agrega filas extra por defecto
    fields = ('numero', 'estado', 'codigo_pago')  # Campos que quieres mostrar
    readonly_fields = ('numero',)  # Haz que el campo `numero` sea de solo lectura
    can_delete = False  # Evita eliminar números directamente desde el admin


@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_termino', 'estado', 'cantidad_numeros')
    inlines = [NumeroInline]  # Asocia los números como un inline para rifas


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'rifa', 'codigo_pago', 'fecha_compra')
    filter_horizontal = ('numeros_comprados',)  # Facilita la selección de números


@admin.register(Ganador)
class GanadorAdmin(admin.ModelAdmin):
    list_display = ('compra', 'premio', 'fecha_ganador')


@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rifa', 'descripcion')


# Si necesitas listar los números globalmente
@admin.register(Numero)
class NumeroAdmin(admin.ModelAdmin):
    list_display = ('numero', 'estado', 'rifa', 'codigo_pago')
    list_filter = ('estado', 'rifa')  # Filtros para reducir la lista