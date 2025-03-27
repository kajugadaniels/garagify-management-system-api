from base.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'base'

urlpatterns = [
    path('inventories/', GetInventory.as_view(), name='GetInventory'),
    path('inventory/add/', AddInventory.as_view(), name='AddInventory'),
    path('inventory/<int:pk>/', InventoryDetails.as_view(), name='InventoryDetails'),
    path('inventory/<int:pk>/update/', UpdateInventory.as_view(), name='UpdateInventory'),
    path('inventory/<int:pk>/delete/', DeleteInventory.as_view(), name='DeleteInventory'),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
