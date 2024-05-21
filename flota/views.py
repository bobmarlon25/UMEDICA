from django.shortcuts import render,redirect
# Create your views here.
from .forms import SubirDumentoImagenForm
from .models import Registros,Ambulancia,Correctivo
from django.contrib.auth.models import User
# from .models import Registros    SubirDumentoImagen
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .utils import render_to_pdf

from django.views.generic import View


from datetime import datetime 
from django.db.models import Sum

from io import BytesIO # nos ayuda a convertir un html en pdf
from django.template.loader import get_template
from xhtml2pdf import pisa
import os 
from django.conf import settings
from django.contrib.staticfiles import finders



    
@login_required
def Registrar(request):
    lista_ambulancias=Ambulancia.objects.all()
    context={
       "ambulancias":lista_ambulancias
    }
   
    return render(request, 'flota/registrar.html',context)



# @login_required
# def Cargar_c(request,ambulancia_id):
#     movil = Ambulancia.objects.get(pk=ambulancia_id)
#     if request.method == "POST":
#         form = SubirDumentoImagenForm(request.POST, request.FILES)
        
         
#         if form.is_valid():
#             # Obtenemos el usuario actualmente autenticado
#             usuario_autenticado = request.user
            
#             # Creamos una instancia del modelo con los datos del formulario
#             instancia = form.save(commit=False)
            
#             # Asignamos el usuario como autor de la instancia
#             instancia.autor = usuario_autenticado
#             instancia.movil=movil
            
            
#             # Guardamos la instancia en la base de datos
#             instancia.save()
#             form.save()
#         return redirect("informacion",ambulancia_id=movil.id)
 


def Infamb(request,ambulancia_id):
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
   
    context = {
        "ambulancia":objambulancia,
    }
    return render(request, 'flota/informacion.html',context)



# Create your views here.
class informetanqueoPdf(View):

    def get(self, request,ambulancia_id,id, *args, **kwargs):
        listaregistro = Registros.objects.get(pk=id)
        objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        print(listaregistro)
        data = {
        'registro':listaregistro,
        'ambulancia':objambulancia,
        'fecha_actual':fecha_actual,
        }
        pdf = render_to_pdf('flota/lista.html', data)
        return HttpResponse(pdf, content_type='application/pdf')



def render_pdf_view(request,ambulancia_id,id):
    template_path = 'flota/lista.html'
    listaregistro = Registros.objects.get(pk=id)
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    print(listaregistro)
    data = {
        'registro':listaregistro,
        'ambulancia':objambulancia,
        'fecha_actual':fecha_actual,
    }   
    context = data
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise RuntimeError(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path


######## tanqueo #########

"""  mostrar  form de tanqueo """
@login_required
def R_combustible(request,ambulancia_id):
    form = SubirDumentoImagenForm()
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
        'form': form
    }

   
    return render(request, 'flota/r_combustible.html',context)
@login_required
def Cargar_c(request,ambulancia_id):
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    mensaje="no hicimos nada "
    if request.method == "POST": 
        formato=SubirDumentoImagenForm(request.POST,request.FILES)

        if formato.is_valid():
           
            dataregistro =formato.cleaned_data
            nuevoregistro=Registros()
            nuevoregistro.autor=request.user
            nuevoregistro.movil=movil
            nuevoregistro.kilometraje=dataregistro["kilometraje"]
            nuevoregistro.remicion=dataregistro["remicion"]
            nuevoregistro.foto=dataregistro["foto"]
            nuevoregistro.firma=dataregistro["firma"]
            nuevoregistro.fecha_registro=dataregistro["fecha"]
            nuevoregistro.save()
            mensaje="si pudimos"
    context = {
        "mensaje":mensaje,
        "ambulancia":movil,
    }


    return redirect('/flota/informacion/{}'.format(ambulancia_id))
    #render(request, 'flota/informacion.html',context)


"""  mostrar el hitorial de tanqueo"""
def Tanqueo(request,ambulancia_id):
    listaregistro = Registros.objects.filter(movil_id=ambulancia_id)
    # Sumar todos los costos de los registros de tanqueo de la ambulancia
    total_cost = listaregistro.aggregate(Sum('costo'))['costo__sum']
    
    # Manejar el caso donde no hay registros (total_cost será None)
    if total_cost is None:
        total_cost = 0




    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    context = {
        'registros':listaregistro,
        'ambulancia':objambulancia,
        'fecha_actual':fecha_actual,
        'total':total_cost,

    }
    return render(request,'flota/historial_tanqueo.html',context)
"""  mostrar  la busqueda de tanqueo """
def B_tanqueo(request,ambulancia_id):
    fecha=request.POST['fecha']
    

    listaregistro = Registros.objects.filter(movil_id=ambulancia_id)
    busqueda = listaregistro.filter(fecha_registro=fecha)
    
    
    
    
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    
    context = {
        'registros':busqueda,
        'ambulancia':objambulancia,
    }
    return render(request,'flota/historial_tanqueo.html',context)



def Busqueda(request,ambulancia_id):
    fecha_1=request.POST['fecha_1']
    fecha_2=request.POST['fecha_2']


    # startdate = date.today()
    # enddate = startdate + timedelta(days=6)
    

    listaregistro = Registros.objects.filter(fecha_registro__range=[fecha_1, fecha_2])
                                                             

    busqueda = listaregistro.filter(movil_id=ambulancia_id)
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    
    context = {
        'registros':busqueda,
        'ambulancia':objambulancia,
    }
    return render(request,'flota/historial_tanqueo.html',context)



"""  mostrar  la informacion del registro del tanqueo  """
def tanqueo_info(request,ambulancia_id,id):
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    objregistro = Registros.objects.get(pk=id)
    context = {
        "ambulancia":objambulancia,
        "registro":objregistro
    }
    return render(request, 'flota/comprobante_tanqueo.html',context)


######## mantenimiento  #########

"""  mostrar  form de tanqueo """
@login_required
def R_mantenimiento(request,ambulancia_id):
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/R_MANTENIMIENTO.html',context)

def historial_mantenimiento(request,ambulancia_id):
    listaregistro = Correctivo.objects.filter(movil_id=ambulancia_id)
    
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    context = {
        'registros':listaregistro,
        'ambulancia':objambulancia,
        'fecha_actual':fecha_actual,

    }
    return render(request,'flota/hist_mantenimiento.html',context)


def mantenimiento_info(request,ambulancia_id,id):
    objambulancia = Ambulancia.objects.get(pk=ambulancia_id)
    objregistro = Correctivo.objects.get(pk=id)
    context = {
        "ambulancia":objambulancia,
        "registro":objregistro
    }
    return render(request, 'flota/comprobante_mantenimiento.html',context)

   
@login_required #1
def R_motor(request,ambulancia_id):
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_motor.html',context)

@login_required#2
def R_sist_combustible(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_sist_combustible.html',context)
     
@login_required#3
def R_interiores(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_interiores.html',context)


@login_required#4
def R_carroceria(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_carroceria.html',context)

@login_required#5
def R_sist_electrico(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_sist_electrico.html',context)

@login_required#6
def R_sist_frenado(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_sist_frenos.html',context)

@login_required#7
def R_sist_suspension(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_sist_suspension.html',context)
 
@login_required#8
def R_sist_transmision(request,ambulancia_id): 
    objambulancia= Ambulancia.objects.get(pk=ambulancia_id)
    context = {
        "movil":objambulancia,
    }  
    return render(request, 'flota/registro_transmision.html',context)
 

"""  recoger la info  de tanqueo """


@login_required #1
def G_motor(request,ambulancia_id):
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    
    
    if request.method == "POST": 
        
        autor = request.user
        movil =movil
        
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="mantenimiento del motor"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()
       
    return redirect('/flota/informacion/{}'.format(ambulancia_id))

@login_required#2
def G_sist_combustible(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    
    
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="sistema combustion"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))
     
@login_required#3
def G_interiores(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="interiores y confort"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))


@login_required#4
def G_carroceria(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="carroceria y exterior"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))

@login_required#5
def G_sist_electrico(request,ambulancia_id):
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="sistema electrico"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))

@login_required#6
def G_sist_frenado(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="sistema de frenado"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))

@login_required#7
def G_sist_suspension(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="sistema de suspencion"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))

@login_required#8
def G_sist_transmision(request,ambulancia_id): 
    movil = Ambulancia.objects.get(pk=ambulancia_id)
    if request.method == "POST": 
        
        autor = request.user
        movil =movil  
        fecha_registro=request.POST['fecha']
        mantenimiento_sistema="trasmicion"
        clase_sistema=request.POST['motor']
        detalle_mantenimiento=request.POST['Parte del Motor:']
        repuesto=request.POST['detalle']
        lugar=request.POST['lugar']
        costo=request.POST['costo']
        kilometraje =request.POST['kilometraje']
        numero_factura=request.POST['numero_factura']
        foto_factura=request.FILES['foto_factura']
        
        nuevoregistro=Correctivo()
        nuevoregistro.autor = autor
        nuevoregistro.movil =movil
        nuevoregistro.fecha_registro=fecha_registro
        nuevoregistro.mantenimiento_sistema=mantenimiento_sistema
        nuevoregistro.clase_sistema=clase_sistema
        nuevoregistro.detalle_mantenimiento=detalle_mantenimiento
        nuevoregistro.repuesto=repuesto
        nuevoregistro.lugar=lugar
        nuevoregistro.costo=costo
        nuevoregistro.kilometraje =kilometraje
        nuevoregistro.numero_factura =numero_factura
        nuevoregistro.foto_factura =foto_factura
        nuevoregistro.save()

    return redirect('/flota/informacion/{}'.format(ambulancia_id))