from ticket.models import Ticket_Cab, Proveedores, Ticket_det
from django import forms
from django.forms import formset_factory, inlineformset_factory
import datetime
import pytz

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedores

        exclude = ['created_at', 'created_by', 'last_modified_at', 'last_modified_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['documento'].widget.attrs.update({'class': 'form-control input-lg'})

class TicketHeaderForm(forms.ModelForm):
    class Meta:
        model = Ticket_Cab
        fields = ['proveedor', 'tipo_de_recoleccion', 'estado','nro_ticket','fecha_ingreso','fecha_salida', 'chofer', 'matricula']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ultimoRegistroTicketCab = Ticket_Cab.objects.last()

        # Control que agregamso por si el ticket es nuevo para agregar por defecto 1000
        self.fields['nro_ticket'].widget.input_type = 'hidden'
        if ultimoRegistroTicketCab is not None:
            self.fields['nro_ticket'].initial =  str(Ticket_Cab.objects.last().nro_ticket + 1)
        else:
            self.fields['nro_ticket'].initial = "1000"

        if self.instance.pk:
            self.fields['estado'].widget.attrs.update({'class': ''})
        else:
            self.fields['estado'].widget.attrs.update({'class': '', 'onclick': "return false"})

        # fechas -- Fecha ingreso
        now = datetime.datetime.now()
        utc_now = now.astimezone(pytz.utc)
        self.fields['fecha_ingreso'].widget.input_type = 'hidden'
        self.initial['fecha_ingreso'] = utc_now.astimezone(pytz.timezone('America/New_York'))

        self.fields['fecha_salida'].widget.input_type = 'hidden'
        self.initial['fecha_salida'] = utc_now.astimezone(pytz.timezone('America/New_York'))

        self.fields['proveedor'].widget.attrs.update(
            {'class': 'selectpicker form-control', "data-live-search": "true", "data-show-subtext": "true"})
        self.fields['tipo_de_recoleccion'].widget.attrs.update(
            {'class': 'selectpicker form-control', "data-live-search": "true", "data-show-subtext": "true"})
        self.fields['chofer'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['matricula'].widget.attrs.update({'class': 'form-control input-lg'})

class TicketDetailForm(forms.ModelForm):
    class Meta:
        model = Ticket_det
        fields = ['producto', 'peso1', 'peso2', 'peso_bruto']
        exclude = ['created_at', 'created_by', 'last_modified_at', 'last_modified_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].widget.attrs.update({'class': 'form-control'})
        self.fields['peso1'].widget.attrs.update({'class': 'form-control','disabled': True})
        self.fields['peso2'].widget.attrs.update({'class': 'form-control','disabled': True})
        self.fields['peso_bruto'].widget.attrs.update({'class': 'form-control','disabled': True})
        # self.fields['ticketCabId'].widget.input_type = 'hidden' 'disabled': True

TicketDetailFormSet = inlineformset_factory(
    Ticket_Cab,
    Ticket_det,
    form=TicketDetailForm,
    extra=5,
    can_delete=True,   # Set this to True if you want to allow deletes
    fields=['id','producto', 'peso1', 'peso2', 'peso_bruto']
)