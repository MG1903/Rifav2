from django.db import models
import random
from django.forms import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Rifa(models.Model):
    ESTADOS = [
        ('oculta', 'Oculta'),
        ('disponible', 'Disponible'),
        ('finalizada', 'Finalizada'),
        ('anulada', 'Anulada'),
    ]

    nombre = models.CharField(max_length=255)
    fecha_inicio = models.DateTimeField()
    fecha_termino = models.DateTimeField()
    descripcion = models.TextField()
    cantidad_numeros = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS)
    imagen = models.ImageField(upload_to='rifas/')

    def clean(self):
        if self.fecha_termino <= self.fecha_inicio:
            raise ValidationError('La fecha de término debe ser posterior a la fecha de inicio.')

    def save(self, *args, **kwargs):
        # Guarda el estado anterior para verificar cambios
        estado_anterior = Rifa.objects.filter(pk=self.pk).values_list('estado', flat=True).first() if self.pk else None
        super().save(*args, **kwargs)

        # Genera números solo si la rifa está disponible
        if estado_anterior is None and self.estado == 'disponible':
            self.generar_numeros()

        # Selecciona ganadores si el estado cambia a "finalizada"
        if estado_anterior != 'finalizada' and self.estado == 'finalizada':
            self.seleccionar_ganadores()

    def generar_numeros(self):
        for i in range(1, self.cantidad_numeros + 1):
            Numero.objects.get_or_create(rifa=self, numero=i)

    def seleccionar_ganadores(self):
        compras = Compra.objects.filter(rifa=self)
        numeros_comprados = []

        for compra in compras:
            numeros_comprados.extend(compra.numeros_comprados.values_list('numero', flat=True))

        # Asegúrate de que los números comprados sean únicos
        numeros_comprados = list(set(numeros_comprados))

        if not numeros_comprados:
            return  # No hay números comprados

        # Obtener los premios relacionados solo con esta rifa
        premios = Premio.objects.filter(rifa=self)
        premios_list = list(premios.values_list('nombre', flat=True))

        if not premios_list:
            return  # No hay premios disponibles

        # Seleccionar ganadores aleatoriamente
        ganadores = random.sample(numeros_comprados, min(len(premios_list), len(numeros_comprados)))

        for ganador_numero in ganadores:
            compra = Compra.objects.filter(numeros_comprados__numero=ganador_numero, rifa=self).first()
            if compra:
                # Crear un nuevo registro en el modelo Ganador
                premio_asignado = premios_list[ganadores.index(ganador_numero)]
                Ganador.objects.create(compra=compra, premio=premio_asignado)

    def __str__(self):
        return self.nombre

class Premio(models.Model):
    rifa = models.ForeignKey(Rifa, related_name='premios', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='premios/')

    def __str__(self):
        return self.nombre
    
class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Numero(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('pagado', 'Pagado'),
    ]

    rifa = models.ForeignKey(Rifa, related_name='numeros', on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='disponible')
    codigo_pago = models.CharField(max_length=10, blank=True, null=True)

    def hacer_disponible(self):
        self.estado = 'disponible'
        self.save()
    
    class Meta:
        # Garantiza que cada número sea único dentro de una rifa
        unique_together = ('rifa', 'numero')
        
    def __str__(self):
        return f"{self.numero} - {self.estado}"
    
def crear_numeros_para_rifa(sender, instance, created, **kwargs):
    if created:
        numeros = [Numero(rifa=instance, numero=i) for i in range(1, instance.cantidad_numeros + 1)]
        Numero.objects.bulk_create(numeros)
    
class Compra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE)
    numeros_comprados = models.ManyToManyField('Numero')
    codigo_pago = models.CharField(max_length=10, blank=True, null=True)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        for numero in self.numeros_comprados.all():
            if numero.estado in ['pagado', 'reservado']:
                numero.hacer_disponible()

        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f"N {self.cliente.nombre} para {self.rifa.nombre}"
    
class Ganador(models.Model):
    compra = models.ForeignKey('Compra', on_delete=models.CASCADE)
    premio = models.CharField(max_length=100)
    fecha_ganador = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.compra.cliente.nombre} ganó {self.premio} con el número {self.compra.numeros_comprados}"
    


