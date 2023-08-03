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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Ticket_Cab

from ticket.forms import ProveedorForm, TicketHeaderForm, TicketDetailFormSet, TicketDetailForm
from ticket.models import Ticket_Cab, Proveedores, Ticket_det

from reportlab.platypus import Table, TableStyle

import socket
import threading
import serial

import websocket
from django.http import JsonResponse


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
# class TicketUpdateView(UpdateView):
#     model = Ticket_Cab
#     fields = ['proveedor', 'tipo_de_recoleccion', 'estado', 'created_by']
#
#     def get(self, request, *args, **kwargs):
#         header_form = TicketHeaderForm()
#         detail_formset = TicketDetailFormSet()
#
#         return render(request, 'modificar_ticket.html', {'header_form': header_form, 'detail_formset': detail_formset})
#
#     def post(self, request):
#         self.object = self.get_object()
#         header_form = TicketHeaderForm(request.POST, instance=self.object)
#         detail_formset = TicketDetailFormSet(request.POST, instance=self.object)
#
#         if header_form.is_valid() and detail_formset.is_valid():
#             header = header_form.save(commit=False)
#             header.created_by = request.user
#             header.save()
#             details = detail_formset.save(commit=False)
#
#             for detail in details:
#                 detail.created_by = request.user
#                 detail.ticketCabId = header
#                 detail.save()
#             else:
#                 print("header_form errors:", header_form.errors)
#                 print("detail_formset errors:", [form.errors for form in detail_formset])
#             return redirect('panel-principal')
#
#         return redirect('panel-principal')












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





# def generar_pdf_and_update_estado(request, id):
#     # Fetch the specific Ticket_Cab record from the model using get_object_or_404
#     ticket_cab = get_object_or_404(Ticket_det, ticketCabId=id)
#     ticket_det = get_object_or_404(Ticket_Cab, pk=id)

#     # Change the estado field to False
#     ticket_det.estado = False
#     ticket_det.save()

#     # Create a response object with PDF content type
#     response = HttpResponse(content_type='application/pdf')

#     # Set the filename for the PDF
#     response['Content-Disposition'] = f'attachment; filename="data_report_{id}.pdf"'

#     # Create a PDF canvas
#     pdf = canvas.Canvas(response, pagesize=letter)

#     # Add content to the PDF
#     pdf.drawString(100, 700, f"Proveedor: {ticket_cab.peso1}")
#     pdf.drawString(100, 680, f"Tipo de recoleccion: {ticket_cab.peso2}")
    
    

#     # Save the PDF content
#     pdf.save()

#     #return redirect('panel-principal')
#     return response



def generar_pdf_actualizar_estado(request, id):
    # Fetch the specific Ticket_Cab record from the model using get_object_or_404
    ticket_cab = get_object_or_404(Ticket_Cab, pk=id)
    ticket_det_list = Ticket_det.objects.filter(ticketCabId=id)

    # Cambio el estado a False del Ticket_Cab
    ticket_cab.estado = False
    ticket_cab.save()

    # Creo el objeto de tipo response con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')

    # Ponemos el nombre del PDF
    response['Content-Disposition'] = f'attachment; filename="ticket_numero_{id}.pdf"'

    # Creamos la estructura del PDF
    pdf = canvas.Canvas(response, pagesize=letter)

    # Agregamos contenido al PDF
    pdf.drawString(100, 700, f"Proveedor: {ticket_cab.proveedor}")
    pdf.drawString(100, 680, f"Tipo de recoleccion: {ticket_cab.tipo_de_recoleccion}")

    
    # Creamos una tabla con los headers y las filas de datos
    table_data = [['Producto', 'Peso1', 'Peso2']]
    for ticket_det in ticket_det_list:
        table_data.append([ticket_det.producto, ticket_det.peso1, ticket_det.peso2])

    table = Table(table_data)

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
    table.wrapOn(pdf, 500, 100)
    table.drawOn(pdf, 100, 600)

    # Guardamos el pdf
    pdf.save()

    return response



# Conexión a la báscula

# def connect_to_websocket(request):
#     websocket_server_url = '10.20.1.125:8059'  # Replace this with the WebSocket server URL
#     print('estoy aqui')
#     try:
#         print('hola')
#         # Connect to the WebSocket server
#         ws = websocket.create_connection(websocket_server_url)
#         print(ws)
        
#         # Send data to the WebSocket server (optional)
#         data_to_send = 'Leer bascula'
#         sendmsg = data_to_send.encode('ascii')
#         hola = ws.send(sendmsg)
        
#         print(hola)

#         # Receive data from the WebSocket server (optional)
#         response_data = ws.recv()

#         # Close the WebSocket connection
#         ws.close()

#         return JsonResponse({'response': response_data})
#     except websocket.WebSocketException as e:
#         return JsonResponse({'error': str(e)})


import socket

def LeerPeso(request):
    print('hola')
    """Main function."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(client)
    client.connect(("10.20.1.125", 8059))
    message = "Leer bascula"
    
    #convert = message.encode('ascii')
    #send_message(client, convert)
    client.sendall(message.encode('ascii'))
    #message = receive_message(client)
    message = client.recv(1024).decode()
    if message == '0':
        message = '0'    
    else:
        print(message)
    client.close()

    return JsonResponse({'message': message})
    # context = {'message': message}
    # return render(request, 'modificar_ticket.html', context)
    
    # return HttpResponse(message)


# def hola(request):
#     # Connect to the server
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(("10.20.1.125", 8059))

#     # Send a message to the server
#     message = "Leer bascula"
#     client.sendall(message.encode('ascii'))

#     # Receive the response from the server
#     response = client.recv(1024).decode()
#     client.close()

#     # Process the response and return it as an HttpResponse
#     if response == '0':
#         response_message = 'Received 0 from server'
#     else:
#         response_message = f'Received: {response} from server'

#     return HttpResponse(response_message)
 


