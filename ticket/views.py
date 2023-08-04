import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView 
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from .models import Ticket_Cab
from ticket.forms import ProveedorForm, TicketHeaderForm, TicketDetailFormSet
from ticket.models import Ticket_Cab, Proveedores, Ticket_det 
from reportlab.platypus import Table, TableStyle 
import socket 
from django.http import JsonResponse  
from django.db.models import Sum


# Create your views here.
def home(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect("panel-principal")
            else:
                messages.error(request, "Usuario y contraseña inválido")
        else:
            messages.error(request, "Usuario y contraseña inválido")
    form = AuthenticationForm()

    return render(request=request, template_name="home.html", context={"login_form": form})


def logout(request):
    logout(request)
    return redirect("home")


@method_decorator(login_required, name='dispatch')
class panel_principal(ListView):
    model = Ticket_Cab
    context_object_name = 'TicketCabView'
    paginate_by = 10
    template_name = 'panel_principal.html'














class TicketCreateView(CreateView):
    model = Ticket_Cab
    fields = ['proveedor', 'tipo_de_recoleccion', 'estado', 'created_by']

    def get(self, request):
        header_form = TicketHeaderForm()
        detail_formset = TicketDetailFormSet()
        return render(request, 'nuevo.html', {'header_form': header_form, 'detail_formset': detail_formset})

    def post(self, request):
        header_form = TicketHeaderForm(request.POST)
        detail_formset = TicketDetailFormSet(request.POST)
        if header_form.is_valid() and detail_formset.is_valid():
            header = header_form.save(commit=False)
            header.created_by = request.user
            
            header.save()
        for cleaned_data in detail_formset.cleaned_data:
            if cleaned_data:
                print('for1')
                details = Ticket_det(
                    producto=cleaned_data['producto'],
                    peso1=cleaned_data['peso1'],
                    peso2=cleaned_data['peso2'],
                    peso_bruto=cleaned_data['peso_bruto'],
                )
                details.invoice_header = header
                details.created_by = request.user
                details.ticketCabId = header
                details.save()

        return redirect('panel-principal')


class TicketUpdateView(UpdateView):
    model = Ticket_Cab
    fields = ['proveedor', 'tipo_de_recoleccion', 'estado', 'created_by']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        header_form = TicketHeaderForm(instance=self.object)
        detail_formset = TicketDetailFormSet(instance=self.object)
        ticket_cab_id = self.object.id  # Access the id directly from the object
        print(ticket_cab_id)  # Print the ticket_cab_id
        return render(request, 'modificar_ticket.html', {'header_form': header_form, 'detail_formset': detail_formset, 'ticket_cab_id': ticket_cab_id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        header_form = TicketHeaderForm(request.POST, instance=self.object)
        detail_formset = TicketDetailFormSet(request.POST, instance=self.object)
        if header_form.is_valid() and detail_formset.is_valid():
            header = header_form.save(commit=False)
            header.created_by = request.user
            header.last_modified_by = request.user
            header.save()
            details = detail_formset.save(commit=False)
            for detail in details:
                detail.created_by = request.user
                detail.last_modified_by = request.user
                detail.ticketCabId = header
                detail.save()
        else:
            print("header_form errors:", header_form.errors)
            print("detail_formset errors:", [form.errors for form in detail_formset])

        return redirect('panel-principal')
 
 
@method_decorator(login_required, name='dispatch')
class panel_proveedores(ListView):
    model = Proveedores
    context_object_name = 'ProveedoresView'
    paginate_by = 10
    template_name = 'proveedores.html'


@method_decorator(login_required, name='dispatch')
class nuevo_proveedor(CreateView):
    model = Proveedores
    form_class = ProveedorForm
    template_name = "nuevo_proveedor.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        return super().form_valid(form)

    success_url = reverse_lazy('panel-proveedores')


@method_decorator(login_required, name='dispatch')
class modificar_proveedor(UpdateView):
    model = Proveedores
    form_class = ProveedorForm
    template_name = 'modificar_proveedor.html'

    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user

        return super().form_valid(form)

    success_url = reverse_lazy('panel-proveedores')

 

def generar_pdf_actualizar_estado(request, id):
    # Fetch the specific Ticket_Cab record from the model using get_object_or_404
    ticket_cab = get_object_or_404(Ticket_Cab, pk=id) 
    ticket_det_list = Ticket_det.objects.filter(ticketCabId=id)

    # total_peso1 = sum(ticket_det_list.peso1.all())
    total_peso1 = ticket_det_list.aggregate(total_peso1=Sum('peso1'))['total_peso1']
    total_peso2 = ticket_det_list.aggregate(total_peso2=Sum('peso2'))['total_peso2']
    total_peso_bruto = ticket_det_list.aggregate(total_peso_bruto=Sum('peso_bruto'))['total_peso_bruto']

    # Cambio el estado a False del Ticket_Cab
    ticket_cab.estado = False
    ticket_cab.save()

    # Creo el objeto de tipo response con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')

    # Ponemos el nombre del PDF
    response['Content-Disposition'] = f'attachment; filename="ticket_numero_{id}.pdf"'

    # Creamos la estructura del PDF
    pdf = canvas.Canvas(response, pagesize=landscape(letter))
 
    left_margin, bottom_margin, right_margin, top_margin = 50, 50, 50, 50

     # Agrega una imagen al PDF 
    imagen_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'yr.png')
    pdf.drawImage(imagen_path, 30, 550, width=180, height=50)

     
    # Agregamos contenido al PDF
    pdf.drawString(left_margin + 25, letter[0] - top_margin - 30, f"Procesado por: {ticket_cab.created_by}")
    pdf.drawString(left_margin + 25, letter[0] - top_margin - 50, f"Impreso por: { request.user }")
    pdf.drawString(left_margin + 400, letter[0] - top_margin - -10, f"Nro. Ticket: {ticket_cab.nro_ticket}")
    pdf.drawString(left_margin + 400, letter[0] - top_margin - 10, f"Empresa: {ticket_cab.proveedor}")
    pdf.drawString(left_margin + 400, letter[0] - top_margin - 30, f"Matricula: {ticket_cab.matricula}")
    pdf.drawString(left_margin + 400, letter[0] - top_margin - 50, f"Chofer: {ticket_cab.chofer}")

    
    
    # Creamos una tabla con los headers y las filas de datos
    table_data = [['Producto', 'Peso1', 'Peso2', 'Peso Bruto']]
    for ticket_det in ticket_det_list:
        table_data.append([ticket_det.producto, ticket_det.peso1, ticket_det.peso2, ticket_det.peso_bruto])

    table_data.append(["Total", total_peso1, total_peso2, total_peso_bruto])

     # Calculate column widths
    num_cols = len(table_data[0])
    table_width = 680  # Total width of the page in points (letter size is 612x792 points)
    col_width = table_width / num_cols
    col_widths = [col_width] * num_cols
    table = Table(table_data, colWidths=col_widths)
    # table = Table(table_data)

    # Damos estilo a la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), 'grey'),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),    # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),    # Header padding
        ('BACKGROUND', (0, 1), (-1, -1), 'white'),  # Data background color
        ('GRID', (0, 0), (-1, -1), 1, 'black'),    # Table grid color
        
    ])
    table.setStyle(style)

    # Dibujamos la tabla en el PDF
    table.wrapOn(pdf, 400, 50)
    table.drawOn(pdf, 50, 400)

    # Guardamos el pdf
    pdf.save()

    return response

 
def LeerPeso(request):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(client)
    client.connect(("10.20.1.125", 8059))
    message = "Leer bascula"
     
    client.sendall(message.encode('ascii')) 
    message = client.recv(1024).decode()
    if message == '0':
        message = '0'    
    else:
        print(message)
    client.close()

    return JsonResponse({'message': message})
 


