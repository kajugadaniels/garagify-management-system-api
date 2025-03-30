from base.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'base'

urlpatterns = [
    path('users/', GetUsers.as_view(), name='GetUsers'),
    path('user/add/', AddUser.as_view(), name='AddUser'),
    path('user/<int:pk>/', UserDetails.as_view(), name='UserDetails'),
    path('user/<int:pk>/update/', UpdateUser.as_view(), name='UpdateUser'),
    path('user/<int:pk>/delete/', DeleteUser.as_view(), name='DeleteUser'),

    path('customers/', GetCustomers.as_view(), name='GetCustomers'),
    path('customer/add/', AddCustomer.as_view(), name='AddCustomer'),
    path('customer/<int:pk>/', CustomerDetails.as_view(), name='CustomerDetails'),
    path('customer/<int:pk>/update/', UpdateCustomer.as_view(), name='UpdateCustomer'),
    path('customer/<int:pk>/delete/', DeleteCustomer.as_view(), name='DeleteCustomer'),

    path('vehicles/', GetVehicles.as_view(), name='GetVehicles'),
    path('vehicle/add/', AddVehicle.as_view(), name='AddVehicle'),
    path('vehicle/<int:pk>/', VehicleDetails.as_view(), name='VehicleDetails'),
    path('vehicle/<int:pk>/update/', UpdateVehicle.as_view(), name='UpdateVehicle'),
    path('vehicle/<int:pk>/delete/', DeleteVehicle.as_view(), name='DeleteVehicle'),

    path('inventories/', GetInventory.as_view(), name='GetInventory'),
    path('inventory/add/', AddInventory.as_view(), name='AddInventory'),
    path('inventory/<int:pk>/', InventoryDetails.as_view(), name='InventoryDetails'),
    path('inventory/<int:pk>/update/', UpdateInventory.as_view(), name='UpdateInventory'),
    path('inventory/<int:pk>/delete/', DeleteInventory.as_view(), name='DeleteInventory'),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
