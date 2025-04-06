import random
import string
from base.models import *
from base.serializers import *
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError

class GetUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieves all users, excluding superadmin users and users with the role 'Customer'.
        """
        # Exclude superadmin users (assuming is_staff=True) and users with role 'Customer'
        users = User.objects.filter(is_staff=False).exclude(role='Customer').order_by('-id')
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response({
            "detail": "Users retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AddUser(APIView):
    permission_classes = [permissions.AllowAny]

    def generate_random_password(self, length=8):
        """
        Generates a random password with letters and digits.
        The default length is 8 characters.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def send_welcome_email(self, user, password):
        """
        Sends a welcome email to the user including their password in plaintext.
        """
        subject = "Welcome to Our Service!"
        message = f"""
        Hello {user.name},

        Welcome to our service! You have been successfully registered.

        Here are your details:
        Name: {user.name}
        Email: {user.email}
        Phone Number: {user.phone_number}
        Role: {user.role}

        Your temporary password is: {password}

        Please change your password after logging in for the first time.

        Best regards,
        The Team
        """

        from_email = settings.DEFAULT_FROM_EMAIL  # Make sure this is set in your settings.py
        recipient_list = [user.email]
        
        # Send the email using the same logic as PasswordResetRequestView
        send_mail(subject, message, from_email, recipient_list)

    def post(self, request, *args, **kwargs):
        """
        Registers a new user, automatically generates a username and a password, 
        and sends a welcome email to the user.
        """
        data = request.data.copy()

        # Generate a random password
        password = self.generate_random_password()

        # Add password to data to be saved
        data['password'] = password

        # Ensure the serializer is created and password is not included in response
        serializer = UserSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            # Save the user, which will auto-generate the username
            user = serializer.save()

            # Set the raw password and hash it correctly
            user.set_password(password)  # This hashes the password before saving
            user.save()

            # Send the welcome email to the user with plaintext password
            self.send_welcome_email(user, password)

            # We don't send the password back in the response for security reasons
            user_data = serializer.data
            user_data.pop('password', None)

            return Response({
                "detail": "User registered successfully. A welcome email has been sent.",
                "data": user_data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "detail": "User registration failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserDetails(APIView):

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieves detailed information about a specific user based on the provided pk.
        """
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, context={'request': request})
            return Response({
                "detail": "User details retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")

class UpdateUser(APIView):

    def put(self, request, pk, *args, **kwargs):
        """
        Updates an existing user based on the provided data.
        """
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)  # partial=True allows partial updates
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response({
                    "detail": "User updated successfully.",
                    "data": UserSerializer(updated_user).data
                }, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Invalid data provided for user update.")
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")
        except ValidationError as e:
            return Response({
                "detail": "User update failed due to validation errors.",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteUser(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        """
        Deletes an existing user based on the provided pk.
        """
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({
                "detail": "User deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")

class GetCustomers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieves all customers (users with role 'Customer').
        """
        customers = User.objects.filter(role='Customer').order_by('-id')
        serializer = CustomerSerializer(customers, many=True, context={'request': request})
        return Response({
            "detail": "Customers retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AddCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def generate_random_password(self, length=8):
        """
        Generates a random password with letters and digits.
        The default length is 8 characters.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def send_welcome_email(self, user, password):
        """
        Sends a welcome email to the customer including their password in plaintext.
        """
        subject = "Welcome to Our Service!"
        message = f"""
        Hello {user.name},

        You have been successfully registered as a customer.

        Here are your details:
        Name: {user.name}
        Email: {user.email}
        Phone Number: {user.phone_number}
        Role: {user.role}

        Your temporary password is: {password}

        Please change your password after logging in for the first time.

        Best regards,
        The Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

    def post(self, request, *args, **kwargs):
        """
        Registers a new customer by automatically generating a username and password,
        forces the role to 'Customer', and sends a welcome email.
        """
        data = request.data.copy()
        data['role'] = 'Customer'  # force role to 'Customer'
        password = self.generate_random_password()
        data['password'] = password

        serializer = CustomerSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)  # Hash the password before saving
            user.save()
            self.send_welcome_email(user, password)
            user_data = serializer.data
            user_data.pop('password', None)
            return Response({
                "detail": "Customer registered successfully. A welcome email has been sent.",
                "data": user_data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "detail": "Customer registration failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieves detailed information about a specific customer.
        """
        try:
            customer = User.objects.get(pk=pk, role='Customer')
            serializer = CustomerSerializer(customer, context={'request': request})
            return Response({
                "detail": "Customer details retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound(detail="Customer not found.")

class UpdateCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        """
        Updates an existing customer's details.
        """
        try:
            customer = User.objects.get(pk=pk, role='Customer')
            serializer = CustomerSerializer(customer, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                updated_customer = serializer.save()
                return Response({
                    "detail": "Customer updated successfully.",
                    "data": CustomerSerializer(updated_customer, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Invalid data provided for customer update.")
        except User.DoesNotExist:
            raise NotFound(detail="Customer not found.")
        except ValidationError as e:
            return Response({
                "detail": "Customer update failed due to validation errors.",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        """
        Deletes an existing customer.
        """
        try:
            customer = User.objects.get(pk=pk, role='Customer')
            customer.delete()
            return Response({
                "detail": "Customer deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            raise NotFound(detail="Customer not found.")

class GetVehicles(APIView):
    """
    Retrieves all vehicles.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        vehicles = Vehicle.objects.all().order_by('-created_at')
        serializer = VehicleSerializer(vehicles, many=True, context={'request': request})
        return Response({
            "detail": "Vehicles retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AddVehicle(APIView):
    """
    Creates a new vehicle record.
    Expects 'customer_id' along with vehicle details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = VehicleSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            vehicle = serializer.save()
            return Response({
                "detail": "Vehicle created successfully.",
                "data": VehicleSerializer(vehicle, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "detail": "Vehicle creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VehicleDetails(APIView):
    """
    Retrieves detailed information about a specific vehicle.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            raise NotFound(detail="Vehicle not found.")
        serializer = VehicleSerializer(vehicle, context={'request': request})
        return Response({
            "detail": "Vehicle details retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UpdateVehicle(APIView):
    """
    Updates an existing vehicle record.
    Supports partial updates.
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            raise NotFound(detail="Vehicle not found.")
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_vehicle = serializer.save()
            return Response({
                "detail": "Vehicle updated successfully.",
                "data": VehicleSerializer(updated_vehicle, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response({
            "detail": "Vehicle update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteVehicle(APIView):
    """
    Deletes an existing vehicle record.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            raise NotFound(detail="Vehicle not found.")
        vehicle.delete()
        return Response({
            "detail": "Vehicle deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

class GetVehicleIssues(APIView):
    """
    Retrieves all vehicle issues.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        issues = VehicleIssue.objects.all().order_by('-created_at')
        serializer = VehicleIssueSerializer(issues, many=True, context={'request': request})
        return Response({
            "detail": "Vehicle issues retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AddVehicleIssue(APIView):
    """
    Creates a new vehicle issue.
    Expects a write-only field 'vehicle_id' along with issue details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = VehicleIssueSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            issue = serializer.save()
            return Response({
                "detail": "Vehicle issue created successfully.",
                "data": VehicleIssueSerializer(issue, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "detail": "Vehicle issue creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VehicleIssueDetails(APIView):
    """
    Retrieves detailed information about a specific vehicle issue.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            issue = VehicleIssue.objects.get(pk=pk)
        except VehicleIssue.DoesNotExist:
            raise NotFound(detail="Vehicle issue not found.")
        serializer = VehicleIssueSerializer(issue, context={'request': request})
        return Response({
            "detail": "Vehicle issue details retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UpdateVehicleIssue(APIView):
    """
    Updates an existing vehicle issue.
    Supports partial updates.
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            issue = VehicleIssue.objects.get(pk=pk)
        except VehicleIssue.DoesNotExist:
            raise NotFound(detail="Vehicle issue not found.")
        serializer = VehicleIssueSerializer(issue, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_issue = serializer.save()
            return Response({
                "detail": "Vehicle issue updated successfully.",
                "data": VehicleIssueSerializer(updated_issue, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response({
            "detail": "Vehicle issue update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteVehicleIssue(APIView):
    """
    Deletes a specific vehicle issue.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            issue = VehicleIssue.objects.get(pk=pk)
        except VehicleIssue.DoesNotExist:
            raise NotFound(detail="Vehicle issue not found.")
        issue.delete()
        return Response({
            "detail": "Vehicle issue deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

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

class DeleteInventory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        """
        Deletes an existing inventory item based on the provided pk.
        """
        try:
            # Retrieve the inventory item by its primary key (pk)
            inventory = Inventory.objects.get(pk=pk)
            
            # Delete the inventory item
            inventory.delete()
            
            return Response({
                "detail": "Inventory item deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        
        except Inventory.DoesNotExist:
            raise NotFound(detail="Inventory item not found.")
        except Exception as e:
            return Response({
                "detail": "An error occurred while deleting the inventory item.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetVehicleSolutions(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        solutions = VehicleSolution.objects.all().order_by('-solution_date')
        serializer = VehicleSolutionSerializer(solutions, many=True, context={'request': request})
        return Response({
            "detail": "Vehicle solutions retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AddVehicleSolution(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VehicleSolutionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            vehicle_solution = serializer.save()
            return Response({
                "detail": "Vehicle solution created successfully.",
                "data": VehicleSolutionSerializer(vehicle_solution, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "detail": "Vehicle solution creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VehicleSolutionDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            solution = VehicleSolution.objects.get(pk=pk)
        except VehicleSolution.DoesNotExist:
            raise NotFound(detail="Vehicle solution not found.")
        serializer = VehicleSolutionSerializer(solution, context={'request': request})
        return Response({
            "detail": "Vehicle solution details retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UpdateVehicleSolution(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            solution = VehicleSolution.objects.get(pk=pk)
        except VehicleSolution.DoesNotExist:
            raise NotFound(detail="Vehicle solution not found.")
        serializer = VehicleSolutionSerializer(solution, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_solution = serializer.save()
            return Response({
                "detail": "Vehicle solution updated successfully.",
                "data": VehicleSolutionSerializer(updated_solution, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response({
            "detail": "Vehicle solution update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteVehicleSolution(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            solution = VehicleSolution.objects.get(pk=pk)
        except VehicleSolution.DoesNotExist:
            raise NotFound(detail="Vehicle solution not found.")

        # Restore inventory for each solution item before deletion
        for item in solution.solution_items.all():
            inventory_item = item.inventory_item
            try:
                available_quantity = int(inventory_item.quantity)
            except (TypeError, ValueError):
                available_quantity = 0
            inventory_item.quantity = str(available_quantity + item.quantity_used)
            inventory_item.save()

        solution.delete()
        return Response({
            "detail": "Vehicle solution deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

class SettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the singleton settings instance.
        """
        settings_instance = Settings.objects.first()
        if not settings_instance:
            return Response({
                "detail": "Settings not configured yet."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SettingsSerializer(settings_instance, context={'request': request})
        return Response({
            "detail": "Settings retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create settings only if not already set.
        """
        if Settings.objects.exists():
            return Response({
                "detail": "Settings already exist. Use PUT to update."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SettingsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            settings_instance = serializer.save()
            return Response({
                "detail": "Settings created successfully.",
                "data": SettingsSerializer(settings_instance).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "detail": "Failed to create settings.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update the singleton settings instance.
        """
        settings_instance = Settings.objects.first()
        if not settings_instance:
            return Response({
                "detail": "Settings not found. Please create first using POST."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SettingsSerializer(settings_instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_settings = serializer.save()
            return Response({
                "detail": "Settings updated successfully.",
                "data": SettingsSerializer(updated_settings).data
            }, status=status.HTTP_200_OK)

        return Response({
            "detail": "Failed to update settings.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CreateQuotationView(APIView):
    """
    Create a quotation from a given vehicle issue with manually provided mechanic shares.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, issue_id, *args, **kwargs):
        try:
            issue = VehicleIssue.objects.get(id=issue_id)
        except VehicleIssue.DoesNotExist:
            raise NotFound("Vehicle issue not found.")

        if not hasattr(issue, 'solution'):
            return Response({"detail": "No solution found for this vehicle issue."}, status=status.HTTP_400_BAD_REQUEST)

        solution = issue.solution

        if hasattr(solution, 'quotation'):
            return Response({"detail": "Quotation already exists for this solution."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate items total
        item_total = 0
        quoted_items = []
        for item in solution.solution_items.all():
            unit_price = float(item.inventory_item.unit_price or 0)
            total = unit_price * item.quantity_used
            item_total += total
            quoted_items.append({
                "inventory_item": item.inventory_item,
                "quantity_used": item.quantity_used,
                "unit_price": unit_price,
                "item_total": total
            })

        # Receive mechanic shares from request
        input_mechanics = request.data.get('quoted_mechanics', [])
        if not input_mechanics:
            return Response({"detail": "Mechanic labor shares are required."}, status=status.HTTP_400_BAD_REQUEST)

        total_labor_share = sum(float(m.get('labor_share', 0)) for m in input_mechanics)
        labor_cost = float(solution.total_cost or 0)

        if round(total_labor_share, 2) != round(labor_cost, 2):
            return Response({
                "detail": "Total labor share must equal the solution's total labor cost.",
                "expected_labor_total": labor_cost,
                "received_total": total_labor_share
            }, status=status.HTTP_400_BAD_REQUEST)

        grand_total = item_total + labor_cost

        # Create the quotation
        quotation = Quotation.objects.create(vehicle_solution=solution, grand_total=grand_total)

        # Save items
        for item in quoted_items:
            QuotedItem.objects.create(
                quotation=quotation,
                inventory_item=item["inventory_item"],
                quantity_used=item["quantity_used"],
                unit_price=item["unit_price"],
                item_total=item["item_total"]
            )

        # Save manually entered mechanic shares
        for mech_data in input_mechanics:
            try:
                mechanic_id = mech_data['mechanic_id']
                labor_share = float(mech_data['labor_share'])
                mechanic = User.objects.get(id=mechanic_id, role='Mechanic')
            except (KeyError, ValueError, User.DoesNotExist):
                return Response({"detail": f"Invalid mechanic data provided: {mech_data}"}, status=status.HTTP_400_BAD_REQUEST)

            QuotedMechanic.objects.create(
                quotation=quotation,
                mechanic=mechanic,
                labor_share=labor_share
            )

        serializer = QuotationSerializer(quotation, context={'request': request})
        return Response({
            "detail": "Quotation created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class GetQuotationByIssueView(APIView):
    """
    Retrieve quotation details based on vehicle issue ID.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, issue_id, *args, **kwargs):
        try:
            issue = VehicleIssue.objects.get(id=issue_id)
        except VehicleIssue.DoesNotExist:
            raise NotFound("Vehicle issue not found.")

        if not hasattr(issue, 'solution') or not hasattr(issue.solution, 'quotation'):
            return Response({"detail": "Quotation not found for this vehicle issue."}, status=status.HTTP_404_NOT_FOUND)

        quotation = issue.solution.quotation
        serializer = QuotationSerializer(quotation, context={'request': request})
        return Response({
            "detail": "Quotation retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


