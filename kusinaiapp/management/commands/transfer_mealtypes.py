from django.core.management.base import BaseCommand
from kusinaiapp.models import MealType, Dish

class Command(BaseCommand):
    help = "Update old meal types to new meal types and remove the old meal types."

    def handle(self, *args, **kwargs):
        # Mapping old meal types to new meal types
        meal_type_mapping = {
            'Soup': 'Soup and Pasta/Noodles',
            'Pasta/Noodles': 'Soup and Pasta/Noodles',
            'Appetizer and Dessert': ['Appetizer', 'Dessert'],  # Split into two
            'Vegetable Recipes': 'Vegetable Recipe',
            'Meat Recipes': 'Meat Recipe',
            'Seafood': 'Seafood Recipe',
        }

        # Update dish meal types
        for dish in Dish.objects.all():
            old_meal_types = dish.meal_type.all()
            new_meal_types = []

            for old_meal_type in old_meal_types:
                new_meal_type_name = meal_type_mapping.get(old_meal_type.name)
                
                # Check if the mapping is a list (i.e., Appetizer and Dessert)
                if isinstance(new_meal_type_name, list):
                    for meal_name in new_meal_type_name:
                        new_meal_type, created = MealType.objects.get_or_create(name=meal_name)
                        new_meal_types.append(new_meal_type)
                elif new_meal_type_name:
                    new_meal_type, created = MealType.objects.get_or_create(name=new_meal_type_name)
                    new_meal_types.append(new_meal_type)

            # Clear the old meal types and assign the new ones
            dish.meal_type.clear()
            dish.meal_type.add(*new_meal_types)
            dish.save()

        # Remove the old meal types from the database
        old_meal_types = ['Soup', 'Pasta/Noodles', 'Appetizer and Dessert', 'Vegetable Recipes', 'Meat Recipes', 'Seafood']
        MealType.objects.filter(name__in=old_meal_types).delete()

        self.stdout.write(self.style.SUCCESS("Successfully updated meal types and removed old meal types!"))
