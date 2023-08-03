from django.contrib import admin
from django.urls import path
from ticket.views import  home, panel_principal, logout, panel_proveedores, \
    nuevo_proveedor, modificar_proveedor, TicketCreateView, TicketUpdateView
from django.conf import settings
from django.conf.urls.static import static
from ticket import views
from ticket.views import LeerPeso
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('panel_principal',panel_principal.as_view(),name='panel-principal'),
    # path('nuevo_ticket', nuevo_ticket.as_view(), name='nuevo-ticket'),
    path('modificar_ticket/<int:pk>', TicketUpdateView.as_view(), name='modificar-ticket'),
    path('logout', home, name='logout'),
    path('panel_proveedores',panel_proveedores.as_view(),name='panel-proveedores'),
    path('nuevo_proveedor', nuevo_proveedor.as_view(), name='nuevo-proveedor'),
    path('modificar_proveedor/<int:pk>', modificar_proveedor.as_view(), name='modificar-proveedor'),
    path('nuevo_ticket',TicketCreateView.as_view(),name='nuevo-ticket'),
    path('generar-pdf/<int:id>/', views.generar_pdf_actualizar_estado, name='generar-pdf'),
    path('connect_to_websocket/', views.LeerPeso, name='connect_to_websocket'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)