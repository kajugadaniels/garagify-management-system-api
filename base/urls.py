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

    path('inventories/', GetInventory.as_view(), name='GetInventory'),
    path('inventory/add/', AddInventory.as_view(), name='AddInventory'),
    path('inventory/<int:pk>/', InventoryDetails.as_view(), name='InventoryDetails'),
    path('inventory/<int:pk>/update/', UpdateInventory.as_view(), name='UpdateInventory'),
    path('inventory/<int:pk>/delete/', DeleteInventory.as_view(), name='DeleteInventory'),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
