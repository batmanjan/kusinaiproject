from django.core.management.base import BaseCommand
from kusinaiapp.models import Dish, MealType
from datetime import timedelta

class Command(BaseCommand):
    help = 'Import dishes into the database'

    def handle(self, *args, **kwargs):
        # List of recipe data to import
        recipes = [
            {
                "dish_name": "Chicken Peanut Gyoza Recipe",
                "preparation_time": "00:15:00",
                "ingredient_list": [
                    {"ingredient": "2 tbsp. cooking oil", "alternatives": []},
                    {"ingredient": "½ pc. small onion, minced", "alternatives": []},
                    {"ingredient": "125 g. ground chicken", "alternatives": []},
                    {"ingredient": "⅛ cup peanut butter", "alternatives": []},
                    {"ingredient": "½ cup mushrooms, diced", "alternatives": []},
                    {"ingredient": "1 pc. Knorr Chicken Cube", "alternatives": []},
                    {"ingredient": "siomai wrapper", "alternatives": []},
                ],
                "number_of_servings": "4-5",  # Adjusted to 2-3 or 4-5
                "procedure": (
                    "Begin by heating up your pan to medium high heat and pour some oil.\n"
                    "Then, throw in the onion and sauté this until translucent before adding the ground chicken.\n"
                    "Give these a nice sauté until the chicken is cooked through.\n"
                    "Now, you may stir in the peanut butter then add the mushrooms and Knorr Chicken Cube.\n"
                    "Mix this well and give it at least 2 minutes to fully incorporate the flavours together.\n"
                    "Since this is going to be the filling in your siomai wrapper, you’ve got to let this cool down.\n"
                    "The next step is quite exciting! To assemble the siomai, place a teaspoonful of the filling in the wrapper before steaming them.\n"
                    "See the reaction on your family’s faces when you serve this Chicken Peanut Gyoza! You’ll win over their hearts for sure."
                ),
                "nutritional_guide": "A delicious fusion dish.",
                "skills_needed": "Beginner",  # Adjusted to beginner, intermediate, advance
                "age_range_that_can_eat": ["Kids", "Teens", "Adults", "Elderly"],  # Adjusted age range
                "cost": 300,
                "dish_image": "https://assets.unileversolutions.com/recipes-v3/110567-default.jpg",
                "meal_type": ["Appetizer", "Meat Recipes"],  # Adjusted meal type
                "approved": False  # Not approved by default
            },
            {
                "dish_name": "Chicken Kalabasa Curry Gata Recipe",
                "preparation_time": "00:15:00",
                "ingredient_list": [
                    {"ingredient": "3 tbsp. cooking oil", "alternatives": []},
                    {"ingredient": "1 pc. small onion, chopped", "alternatives": []},
                    {"ingredient": "3 cloves garlic, minced", "alternatives": []},
                    {"ingredient": "500 g. chicken fillet, sliced", "alternatives": []},
                    {"ingredient": "½ pc. medium squash, peeled and cubed", "alternatives": []},
                    {"ingredient": "2 ½ cups water", "alternatives": []},
                    {"ingredient": "41 g (1 pack) Knorr Complete Recipe Mix Ginataang Gulay Mix", "alternatives": []},
                    {"ingredient": "2 tbsp. curry powder", "alternatives": []},
                    {"ingredient": "1 pc. Knorr Chicken Cube", "alternatives": []},
                    {"ingredient": "1 pc. green siling haba", "alternatives": []},
                ],
                "number_of_servings": "4-5",  # Adjusted to 2-3 or 4-5
                "procedure": (
                    "Begin by grabbing a pan and getting it nice and hot over medium high heat.\n"
                    "Pour some oil and throw in the onion and garlic and sauté them until the onion is translucent and the garlic is golden in color.\n"
                    "Now, add the chicken and sauté this until the chicken is cooked through.\n"
                    "For the next step, place the squash in the pan then add water, Knorr Complete Recipe Mix Ginataang Gulay, curry powder, Knorr Chicken Cube, and siling haba.\n"
                    "Give these at least 5 minutes or until the squash cubes are fork tender, and then you are done!\n"
                    "Chicken Curry is one of those comfort dishes that you look forward to when coming home because it’s simply addicting.\n"
                    "With the added sweetness of kalabasa, you’ll surely end up eating more."
                ),
                "nutritional_guide": "A flavorful and comforting dish.",
                "skills_needed": "Beginner",  # Adjusted to beginner, intermediate, advance
                "age_range_that_can_eat": ["Kids", "Teens", "Adults", "Elderly"],  # Adjusted age range
                "cost": 400,
                "dish_image": "https://assets.unileversolutions.com/recipes-v3/110571-default.jpg",
                "meal_type": ["Soup", "Meat Recipes"],  # Adjusted meal type
                "approved": False  # Not approved by default
            },
            {
                "dish_name": "Chicken Monggo Recipe",
                "preparation_time": "00:25:00",
                "ingredient_list": [
                    {"ingredient": "3 tbsp. cooking oil", "alternatives": []},
                    {"ingredient": "1 pc. small onion, chopped", "alternatives": []},
                    {"ingredient": "3 cloves garlic, minced", "alternatives": []},
                    {"ingredient": "125 g. chicken, cubed", "alternatives": []},
                    {"ingredient": "4 cups water", "alternatives": []},
                    {"ingredient": "½ cup monggo beans", "alternatives": []},
                    {"ingredient": "½ Knorr Complete Recipe Mix Ginataang Gulay", "alternatives": []},
                    {"ingredient": "¼ cup bagoong", "alternatives": []},
                    {"ingredient": "½ cup malunggay leaves", "alternatives": []},
                ],
                "number_of_servings": "4-5",  # Adjusted to 2-3 or 4-5
                "procedure": (
                    "Heat pan over medium flame, heat oil, then add the onion and garlic and give this a quick sauté until the onion is translucent and the garlic is golden in color.\n"
                    "Now, you can place the chicken on your pan and sauté this until it is cooked through.\n"
                    "Next, pour the water, monggo, Knorr Complete Recipe Mix Ginataang Gulay, bagoong, and malunggay leaves and allow these to simmer for at least 5 minutes.\n"
                    "No fuss! You can get a full and hearty meal in just a few steps!\n"
                    "Enjoy this with family and you will definitely have a conversation starter at the table."
                ),
                "nutritional_guide": "A hearty and nutritious meal.",
                "skills_needed": "Beginner",  # Adjusted to beginner, intermediate, advance
                "age_range_that_can_eat": ["Kids", "Teens", "Adults", "Elderly"],  # Adjusted age range
                "cost": 250,
                "dish_image": "https://assets.unileversolutions.com/recipes-v3/110575-default.jpg",
                "meal_type": ["Soup", "Meat Recipes"],  # Adjusted meal type
                "approved": False  # Not approved by default
            }
        ]

        for recipe_data in recipes:
            # Convert preparation time string to a timedelta object
            preparation_time = timedelta(minutes=int(recipe_data['preparation_time'].split(":")[1]))

            # Retrieve or create the meal types
            meal_types = []
            for meal_type_name in recipe_data['meal_type']:
                meal_type, created = MealType.objects.get_or_create(name=meal_type_name)
                meal_types.append(meal_type)

            # Create or update the Dish object
            dish, created = Dish.objects.update_or_create(
                dish_name=recipe_data['dish_name'],
                defaults={
                    'preparation_time': preparation_time,
                    'ingredient_list': recipe_data['ingredient_list'],
                    'number_of_servings': recipe_data['number_of_servings'],
                    'procedure': recipe_data['procedure'],
                    'nutritional_guide': recipe_data['nutritional_guide'],
                    'skills_needed': recipe_data['skills_needed'],
                    'age_range_that_can_eat': recipe_data['age_range_that_can_eat'],
                    'cost': recipe_data['cost'],
                    'dish_image': recipe_data['dish_image'],
                    'approved': recipe_data['approved'],
                }
            )

            # Add the meal types to the dish
            dish.meal_type.set(meal_types)

            # Save the dish
            dish.save()

            self.stdout.write(self.style.SUCCESS(f"Successfully added/updated dish: {dish.dish_name}"))
