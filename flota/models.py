from django.db import models
from django.contrib.auth.models import User 
from datetime import date
from django.utils import timezone
# Create your models here.



class  Ambulancia(models.Model):
    movil =models.CharField(max_length=100)
    clasevehiculo=models.CharField(max_length=100)
    marca=models.CharField(max_length=100)
    modelo=models.IntegerField(null=False, blank=False)
    placa=models.CharField(max_length=10)
    ven_soat=models.DateField(default=timezone.now)
    ven_tecno=models.DateField(default=timezone.now)
    frontal = models.ImageField(upload_to='media/',blank=True)
    lateral = models.ImageField(upload_to='media/',blank=True)

    def __str__(self):
        return self.movil



class  Registros(models.Model):
    autor = models.ForeignKey(User,on_delete=models.RESTRICT)
   
    fecha_registro=models.DateField(default=timezone.now)
  
    hora_registro = models.DateTimeField(default=timezone.now)
    movil = models.ForeignKey(Ambulancia,on_delete=models.RESTRICT)
    kilometraje = models.IntegerField(null=False, blank=False)
    remicion= models.IntegerField(null=False, blank=False)
    firma = models.ImageField(upload_to='media',blank=True)
    foto = models.ImageField(upload_to='media',blank=True)
   
    def get_last_name(self):
        return self.autor.last_name

    def __str__(self):
        return self.autor.last_name
    



class  Correctivo(models.Model):
    autor = models.ForeignKey(User,on_delete=models.RESTRICT)
    movil = models.ForeignKey(Ambulancia,on_delete=models.RESTRICT)
    hora_registro = models.DateTimeField(default=timezone.now)
    fecha_registro=models.DateField(default=timezone.now)
    mantenimiento_sistema=models.TextField()
    clase_sistema=models.TextField()
    detalle_mantenimiento=models.TextField()
    repuesto=models.CharField(max_length=30)
    lugar=models.TextField()
    costo=models.DecimalField(max_digits=10,decimal_places=2,default=0)

    kilometraje = models.IntegerField(null=False, blank=False)
    numero_factura= models.IntegerField(null=False, blank=False)
    foto_factura= models.ImageField(upload_to='media',blank=True)
   
    
    def __str__(self):
        return self.movil
    