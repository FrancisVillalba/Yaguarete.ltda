from django.db import models
from core.models import CommonInfo

# Create your models here.
class Proveedores(CommonInfo):
    nombre = models.CharField(max_length=255)
    documento = models.CharField(max_length=255, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombre} {self.documento}'


class Productos(CommonInfo):
    nombre = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombre}'


class Tipo_recoleccion(CommonInfo):
    nombre = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nombre}'


class Ticket_Cab(CommonInfo):
    nro_ticket = models.IntegerField(default=0, unique=True)
    fecha_ingreso = models.DateTimeField()
    fecha_salida = models.DateTimeField()
    proveedor = models.ForeignKey(Proveedores, on_delete=models.SET_NULL, null=True)
    chofer = models.CharField(max_length=255, default='', null=True)
    matricula = models.CharField(max_length=255, default='', null=True)
    
    tipo_de_recoleccion = models.ForeignKey(Tipo_recoleccion, on_delete=models.SET_NULL, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'Id: {self.id},  Fecha_ingreso: {self.fecha_ingreso}, Fecha_salida: {self.fecha_salida}, Proveedor: {self.proveedor}, Tipo_recoleccion: {self.tipo_de_recoleccion}'


class Ticket_det(CommonInfo):
    ticketCabId = models.ForeignKey(Ticket_Cab, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(Productos, on_delete=models.SET_NULL, null=True)
    peso1 = models.IntegerField(default=0.0, null=True, blank=True)
    peso2 = models.IntegerField(default=0.0, null=True, blank=True)
    peso_bruto = models.IntegerField(default=0.0, null=True, blank=True)


    def __str__(self):
        return f'Id: {self.id},  Productos: {self.producto}, Peso1: {self.peso1}, Peso2: {self.peso2}, Peso_bruto: {self.peso_bruto}'

    def save(self):
        if (self.peso2 > 0):
            self.peso_bruto = (self.peso1-  self.peso2)

        return super(Ticket_det, self).save()
