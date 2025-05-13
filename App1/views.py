from django.shortcuts import get_object_or_404, redirect, render
from .models import Rifa, Numero, Compra, Cliente, Ganador
from .forms import CompraForm
# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from App1.models import Rifa, Cliente, Numero, Compra


def lista_rifas(request):
    rifas = Rifa.objects.filter(estado='disponible')
    return render(request, 'lista_rifas.html', {'rifas': rifas})

def detalle_rifa(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    numeros_disponibles = rifa.numeros.filter(estado='disponible')
    min_numero = request.GET.get('min_numero')
    max_numero = request.GET.get('max_numero')

    if min_numero and max_numero:
        try:
            min_numero = int(min_numero)
            max_numero = int(max_numero)
            numeros_disponibles = numeros_disponibles.filter(numero__gte=min_numero, numero__lte=max_numero)
        except ValueError:
            pass

    return render(request, 'detalle_rifa.html', {
        'rifa': rifa,
        'numeros': numeros_disponibles,
    })
    
def formulario_compra(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            return redirect('compra_numero', rifa_id=rifa_id)
        else:
            print(form.errors)

    else:
        numeros_seleccionados = request.GET.getlist('numeros')
        form = CompraForm(initial={'numeros_seleccionados': ','.join(numeros_seleccionados)})

    return render(request, 'formulario.html', {'rifa': rifa, 'form': form, 'numeros_seleccionados': numeros_seleccionados})

def compra_numero(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)

    if request.method == 'POST':
        # Datos del cliente
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        numeros_seleccionados = request.POST.get('numeros_seleccionados', '').split(',')
        codigo_pago = request.POST.get('codigo_pago', '')

        # Crear o recuperar cliente
        cliente, created = Cliente.objects.get_or_create(
            email=email,
            defaults={'nombre': nombre, 'telefono': telefono}
        )

        # Validar y limpiar números seleccionados
        numeros_seleccionados = [numero.strip() for numero in numeros_seleccionados if numero.strip()]

        if not numeros_seleccionados:
            return redirect('detalle_rifa', rifa_id=rifa.id)

        numeros_comprados = []
        for numero in numeros_seleccionados:
            # Verificar que el número existe y está disponible
            numero_obj = get_object_or_404(Numero, rifa=rifa, numero=numero, estado='disponible')

            # Cambiar el estado según el pago
            numero_obj.estado = 'pagado' if codigo_pago else 'reservado'
            numero_obj.save()

            # Agregar número al listado de comprados
            numeros_comprados.append(numero_obj)

        # Crear o actualizar la compra
        compra, created = Compra.objects.get_or_create(
            cliente=cliente,
            rifa=rifa,
            defaults={'codigo_pago': codigo_pago if codigo_pago else None}
        )
        compra.numeros_comprados.add(*numeros_comprados)  # Asociar números seleccionados

        # Redirigir a la página de detalle
        return redirect('detalle_rifa', rifa_id=rifa.id)

    return redirect('detalle_rifa', rifa_id=rifa.id)

def validar_codigo_pago(codigo_pago):
    if len(codigo_pago) != 10:
        return False
    if not codigo_pago[:3].isalpha() or not codigo_pago[3:].isdigit():
        return False
    pares = sum(1 for char in codigo_pago[3:] if int(char) % 2 == 0)
    impares = len(codigo_pago[3:]) - pares
    return pares > impares

def mostrar_rifas_finalizadas(request):
    rifas = Rifa.objects.filter(estado='finalizada')
    return render(request, 'rifas_finalizadas.html', {
        'rifas': rifas,
    })

def mostrar_ganadores_por_rifa(request, rifa_id):
    rifa = Rifa.objects.get(id=rifa_id)
    ganadores = Ganador.objects.filter(compra__rifa=rifa).select_related('compra__cliente')

    return render(request, 'ganadores.html', {
        'rifa': rifa,
        'ganadores': ganadores,
    })