from django.core.management.base import BaseCommand
from base.models import Inventory
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = "Generate 50 fake Inventory products for the garage"

    def handle(self, *args, **options):
        fake = Faker()
        ITEM_TYPES = ['Spare Part', 'Tools', 'Materials']
        created_count = 0

        for _ in range(50):
            # Generate a fake product name (e.g., "Brake Pad", "Oil Filter")
            item_name = f"{fake.word().capitalize()} {fake.word().capitalize()}"
            item_type = random.choice(ITEM_TYPES)
            quantity = str(random.randint(1, 300))  # Stored as a string
            unit_price = str(round(random.uniform(10000.0, 50000.0), 2))  # Stored as a string

            # Create inventory object with created_by left as None
            inventory_item = Inventory(
                item_name=item_name,
                item_type=item_type,
                quantity=quantity,
                unit_price=unit_price,
                created_at=timezone.now()
            )
            inventory_item.save()
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} fake inventory items."))
