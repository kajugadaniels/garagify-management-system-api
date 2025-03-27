from base.models import *
from base.serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

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

class InventoryDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieves detailed information about a specific inventory item, including user information.
        """
        try:
            # Retrieve the inventory item by its primary key (pk)
            inventory = Inventory.objects.get(pk=pk)
            
            # Serialize the inventory item data, including the nested created_by user information
            serializer = InventorySerializer(inventory)
            
            return Response({
                "detail": "Inventory details retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except Inventory.DoesNotExist:
            raise NotFound(detail="Inventory item not found.")
        except Exception as e:
            return Response({
                "detail": "An error occurred while retrieving the inventory details.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateInventory(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        """
        Updates an existing inventory item based on the provided data.
        Only fields that are included in the request are updated.
        """
        try:
            # Retrieve the inventory item by its primary key (pk)
            inventory = Inventory.objects.get(pk=pk)
            
            # Pass the request data along with the instance (inventory) to the serializer
            serializer = InventorySerializer(inventory, data=request.data, partial=True)  # partial=True allows partial updates

            if serializer.is_valid():
                # Save the updated inventory item
                updated_inventory = serializer.save()
                return Response({
                    "detail": "Inventory item updated successfully.",
                    "data": InventorySerializer(updated_inventory).data
                }, status=status.HTTP_200_OK)
            else:
                # Raise validation error if the serializer is not valid
                raise ValidationError("Invalid data provided for inventory update.")

        except Inventory.DoesNotExist:
            raise NotFound(detail="Inventory item not found.")
        except ValidationError as e:
            return Response({
                "detail": "Inventory update failed due to validation errors.",
                "errors": e.detail  # This will properly show the validation error messages
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "detail": "An error occurred while updating the inventory item.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)