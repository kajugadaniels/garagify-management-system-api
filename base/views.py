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

class AddInventory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        
        serializer = InventorySerializer(data=data)
        if serializer.is_valid():
            try:
                inventory = serializer.save(created_by=request.user)  # Save with the full user instance
                return Response({
                    "detail": "Inventory created successfully.",
                    "data": InventorySerializer(inventory).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "detail": "An error occurred while creating the inventory.",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "detail": "Inventory creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)