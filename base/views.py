from base.models import *
from base.serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class GetInventory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            inventories = Inventory.objects.all().order_by('-id')
            serializer = InventorySerializer(inventories, many=True)
            return Response({
                "detail": "Inventories retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "detail": "An error occurred while retrieving inventories.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)