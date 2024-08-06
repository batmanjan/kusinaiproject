import os
import django
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_duration
from kusinaiapp.models import Dish
from datetime import timedelta

class Command(BaseCommand):
    help = 'Import dishes into the database'

    def handle(self, *args, **kwargs):
        dishes = [
            {
                "dish_name": "Malunggay Shanghai",
                "preparation_time": timedelta(minutes=90),
                "ingredient_list": "2 kg mussels, 1 cup moringa leaves, 2 pieces carrots (grated), 3 pieces eggs (beaten), 1/2 cup bread crumbs, 1 teaspoon iodized salt, 1/2 teaspoon crushed pepper, 20 pieces lumpia wrappers, 2-3 cups cooking oil",
                "number_of_servings": "2-3",
                "procedure": "Boil the mussels until cooked. Remove from water, take them out of their shells, and chop slightly. Mix the mussels with moringa leaves, carrots, eggs, and bread crumbs. Stir well. Season with iodized salt and crushed pepper to taste. Wrap the mixture in lumpia wrappers and fry in hot oil until golden brown.",
                "nutritional_guide": "Approx. 250 calories per serving. Includes 15 grams of total fat, 3 grams of saturated fat, no trans fats, 50 milligrams of cholesterol, 500 milligrams of sodium, 20 grams of total carbohydrates, 2 grams of dietary fiber, 5 grams of sugars, and 15 grams of protein. Contributes to 10% DV for Vitamin A, 15% for Vitamin C, 8% for Calcium, and 12% for Iron. Contains allergens such as wheat.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Kids", "Teens", "Adults"],
                "cost": "100-200",
                "dish_image": "path/to/malunggay_shanghai.jpg",  # Replace with actual path
                "meal_type": "Appetizer",
            },
            {
                "dish_name": "Chicken Teriyaki",
                "preparation_time": timedelta(minutes=45),
                "ingredient_list": "500 grams chicken breast, 1/4 cup soy sauce, 2 tablespoons brown sugar, 1 tablespoon mirin, 1 tablespoon sake, 2 cloves garlic (minced), 1 teaspoon grated ginger, 1 tablespoon cornstarch, 2 tablespoons water, 2 tablespoons vegetable oil",
                "number_of_servings": "4",
                "procedure": "Mix soy sauce, brown sugar, mirin, sake, garlic, and ginger in a bowl. Marinate chicken in the mixture for at least 30 minutes. Heat oil in a pan and cook chicken until browned. Add the marinade and simmer until the sauce thickens. Mix cornstarch with water and add to the sauce to thicken further.",
                "nutritional_guide": "Approx. 300 calories per serving. Includes 10 grams of total fat, 2 grams of saturated fat, no trans fats, 70 milligrams of cholesterol, 800 milligrams of sodium, 15 grams of total carbohydrates, 1 gram of dietary fiber, 12 grams of sugars, and 35 grams of protein.",
                "skills_needed": "Intermediate",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "300-400",
                "dish_image": "path/to/chicken_teriyaki.jpg",  # Replace with actual path
                "meal_type": "Main Course",
            },
            {
                "dish_name": "Garlic Butter Shrimp",
                "preparation_time": timedelta(minutes=20),
                "ingredient_list": "500 grams shrimp (peeled and deveined), 4 cloves garlic (minced), 1/4 cup butter, 1 tablespoon lemon juice, 1 tablespoon chopped parsley, salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "In a pan, melt butter and add garlic. Sauté until fragrant. Add shrimp and cook until pink. Stir in lemon juice and parsley, and season with salt and pepper.",
                "nutritional_guide": "Approx. 250 calories per serving. Includes 15 grams of total fat, 8 grams of saturated fat, no trans fats, 150 milligrams of cholesterol, 500 milligrams of sodium, 10 grams of total carbohydrates, 1 gram of dietary fiber, 1 gram of sugars, and 25 grams of protein.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "700-800",
                "dish_image": "path/to/garlic_butter_shrimp.jpg",  # Replace with actual path
                "meal_type": "Appetizer",
            },
            {
                "dish_name": "Lemon Blueberry Muffins",
                "preparation_time": timedelta(minutes=35),
                "ingredient_list": "1 1/2 cups all-purpose flour, 1 cup sugar, 1/2 cup butter, 2 eggs, 1/2 cup milk, 1 teaspoon baking powder, 1/2 teaspoon baking soda, 1 cup blueberries, 1 tablespoon lemon zest",
                "number_of_servings": "12",
                "procedure": "Preheat oven to 375°F (190°C). Cream butter and sugar. Add eggs, milk, and lemon zest. Mix in flour, baking powder, and baking soda. Fold in blueberries. Spoon batter into muffin tins and bake for 20-25 minutes.",
                "nutritional_guide": "Approx. 200 calories per muffin. Includes 10 grams of total fat, 6 grams of saturated fat, no trans fats, 50 milligrams of cholesterol, 150 milligrams of sodium, 30 grams of total carbohydrates, 1 gram of dietary fiber, 15 grams of sugars, and 3 grams of protein.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Kids", "Teens", "Adults"],
                "cost": "300-400",
                "dish_image": "path/to/lemon_blueberry_muffins.jpg",  # Replace with actual path
                "meal_type": "Dessert",
            },
            {
                "dish_name": "Roasted Vegetable Soup",
                "preparation_time": timedelta(minutes=45),
                "ingredient_list": "1 cup carrots (chopped), 1 cup potatoes (chopped), 1 cup bell peppers (chopped), 1 onion (chopped), 4 cups vegetable broth, 2 tablespoons olive oil, 1 teaspoon dried thyme, salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "Preheat oven to 400°F (200°C). Toss vegetables with olive oil, thyme, salt, and pepper. Roast for 25-30 minutes. Blend roasted vegetables with vegetable broth until smooth. Heat soup before serving.",
                "nutritional_guide": "Approx. 150 calories per serving. Includes 7 grams of total fat, 1 gram of saturated fat, no trans fats, 0 milligrams of cholesterol, 500 milligrams of sodium, 20 grams of total carbohydrates, 4 grams of dietary fiber, 5 grams of sugars, and 3 grams of protein.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Kids", "Teens", "Adults"],
                "cost": "500-600",
                "dish_image": "path/to/roasted_vegetable_soup.jpg",  # Replace with actual path
                "meal_type": "Soup",
            },
            {
                "dish_name": "Beef Wellington",
                "preparation_time": timedelta(hours=1, minutes=30),
                "ingredient_list": "500 grams beef tenderloin, 1/2 cup pâté, 1 cup mushroom duxelles, 1 sheet puff pastry, 1 egg (beaten), salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "Season beef with salt and pepper, sear in a hot pan. Spread pâté on beef, then mushroom duxelles. Wrap beef in puff pastry and brush with beaten egg. Bake at 400°F (200°C) for 25-30 minutes.",
                "nutritional_guide": "Approx. 600 calories per serving. Includes 40 grams of total fat, 15 grams of saturated fat, no trans fats, 150 milligrams of cholesterol, 600 milligrams of sodium, 30 grams of total carbohydrates, 2 grams of dietary fiber, 5 grams of sugars, and 35 grams of protein.",
                "skills_needed": "Advanced",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "900-1000",
                "dish_image": "path/to/beef_wellington.jpg",  # Replace with actual path
                "meal_type": "Main Course",
            },
            {
                "dish_name": "Greek Salad",
                "preparation_time": timedelta(minutes=15),
                "ingredient_list": "2 cups cherry tomatoes, 1 cucumber (sliced), 1/2 cup red onion (sliced), 1/2 cup Kalamata olives, 1/2 cup feta cheese, 2 tablespoons olive oil, 1 tablespoon red wine vinegar, 1 teaspoon dried oregano, salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "Combine tomatoes, cucumber, red onion, olives, and feta in a bowl. Whisk together olive oil, vinegar, oregano, salt, and pepper. Toss salad with dressing before serving.",
                "nutritional_guide": "Approx. 200 calories per serving. Includes 15 grams of total fat, 3 grams of saturated fat, no trans fats, 25 milligrams of cholesterol, 400 milligrams of sodium, 10 grams of total carbohydrates, 2 grams of dietary fiber, 4 grams of sugars, and 5 grams of protein.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Kids", "Teens", "Adults"],
                "cost": "100-200",
                "dish_image": "path/to/greek_salad.jpg",  # Replace with actual path
                "meal_type": "Vegetable Dishes",
            },
            {
                "dish_name": "Chocolate Lava Cake",
                "preparation_time": timedelta(minutes=25),
                "ingredient_list": "1/2 cup butter, 1 cup dark chocolate, 1 cup powdered sugar, 2 eggs, 2 egg yolks, 1/2 cup all-purpose flour, butter and cocoa powder for greasing molds",
                "number_of_servings": "4",
                "procedure": "Preheat oven to 425°F (220°C). Melt butter and chocolate together. Stir in powdered sugar, then eggs and egg yolks. Fold in flour. Pour into greased molds and bake for 12-14 minutes.",
                "nutritional_guide": "Approx. 400 calories per serving. Includes 25 grams of total fat, 15 grams of saturated fat, no trans fats, 120 milligrams of cholesterol, 200 milligrams of sodium, 40 grams of total carbohydrates, 2 grams of dietary fiber, 30 grams of sugars, and 6 grams of protein.",
                "skills_needed": "Intermediate",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "500-600",
                "dish_image": "path/to/chocolate_lava_cake.jpg",  # Replace with actual path
                "meal_type": "Dessert",
            },
            {
                "dish_name": "Spaghetti Carbonara",
                "preparation_time": timedelta(minutes=30),
                "ingredient_list": "200 grams spaghetti, 100 grams pancetta, 2 eggs, 1 cup grated Parmesan cheese, 2 cloves garlic (minced), 2 tablespoons olive oil, salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "Cook spaghetti according to package instructions. Sauté pancetta in olive oil. Mix eggs and Parmesan cheese. Combine cooked spaghetti with pancetta and garlic. Remove from heat and mix with egg mixture. Season with salt and pepper.",
                "nutritional_guide": "Approx. 400 calories per serving. Includes 20 grams of total fat, 8 grams of saturated fat, no trans fats, 90 milligrams of cholesterol, 600 milligrams of sodium, 45 grams of total carbohydrates, 2 grams of dietary fiber, 2 grams of sugars, and 15 grams of protein.",
                "skills_needed": "Intermediate",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "300-400",
                "dish_image": "path/to/spaghetti_carbonara.jpg",  # Replace with actual path
                "meal_type": "Main Course",
            },
            {
                "dish_name": "Tiramisu",
                "preparation_time": timedelta(minutes=45),
                "ingredient_list": "6 egg yolks, 1 cup sugar, 1 cup mascarpone cheese, 1 cup heavy cream, 1 cup brewed espresso (cooled), 1/4 cup coffee liqueur, 1 package ladyfingers, cocoa powder for dusting",
                "number_of_servings": "8",
                "procedure": "Whisk egg yolks and sugar until thick. Fold in mascarpone cheese. Whip cream and fold into mascarpone mixture. Dip ladyfingers in espresso and liqueur, layer in a dish, and top with mascarpone mixture. Chill for 4 hours and dust with cocoa powder before serving.",
                "nutritional_guide": "Approx. 350 calories per serving. Includes 22 grams of total fat, 13 grams of saturated fat, no trans fats, 130 milligrams of cholesterol, 100 milligrams of sodium, 35 grams of total carbohydrates, 1 gram of dietary fiber, 25 grams of sugars, and 6 grams of protein.",
                "skills_needed": "Advanced",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "700-800",
                "dish_image": "path/to/tiramisu.jpg",  # Replace with actual path
                "meal_type": "Dessert",
            },
            {
                "dish_name": "Quiche Lorraine",
                "preparation_time": timedelta(minutes=50),
                "ingredient_list": "1 pie crust, 6 slices bacon (cooked and crumbled), 1 cup shredded Swiss cheese, 4 eggs, 1 cup heavy cream, 1 cup milk, salt and pepper to taste",
                "number_of_servings": "6",
                "procedure": "Preheat oven to 375°F (190°C). Spread bacon and cheese over pie crust. Whisk eggs, cream, and milk together. Pour over bacon and cheese. Bake for 35-40 minutes or until set.",
                "nutritional_guide": "Approx. 400 calories per serving. Includes 30 grams of total fat, 15 grams of saturated fat, no trans fats, 150 milligrams of cholesterol, 600 milligrams of sodium, 20 grams of total carbohydrates, 1 gram of dietary fiber, 2 grams of sugars, and 15 grams of protein.",
                "skills_needed": "Intermediate",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "500-600",
                "dish_image": "path/to/quiche_lorraine.jpg",  # Replace with actual path
                "meal_type": "Main Course",
            },
            {
                "dish_name": "Ceviche",
                "preparation_time": timedelta(minutes=30),
                "ingredient_list": "500 grams white fish (cubed), 1 cup lime juice, 1/2 cup red onion (diced), 1/2 cup cilantro (chopped), 1 jalapeño (diced), salt and pepper to taste",
                "number_of_servings": "4",
                "procedure": "Marinate fish in lime juice for 20 minutes. Add red onion, cilantro, and jalapeño. Season with salt and pepper. Serve chilled.",
                "nutritional_guide": "Approx. 150 calories per serving. Includes 3 grams of total fat, 0 grams of saturated fat, no trans fats, 50 milligrams of cholesterol, 200 milligrams of sodium, 5 grams of total carbohydrates, 1 gram of dietary fiber, 2 grams of sugars, and 25 grams of protein.",
                "skills_needed": "Beginner",
                "age_range_that_can_eat": ["Teens", "Adults"],
                "cost": "300-400",
                "dish_image": "path/to/ceviche.jpg",  # Replace with actual path
                "meal_type": "Appetizer",
            },
        ]

        for dish in dishes:
            Dish.objects.create(
                dish_name=dish['dish_name'],
                preparation_time=parse_duration(str(dish['preparation_time'])),
                ingredient_list=dish['ingredient_list'],
                number_of_servings=dish['number_of_servings'],
                procedure=dish['procedure'],
                nutritional_guide=dish['nutritional_guide'],
                skills_needed=dish['skills_needed'],
                age_range_that_can_eat=dish['age_range_that_can_eat'],
                cost=dish['cost'],
                dish_image=dish['dish_image'],
                meal_type=dish['meal_type'],
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported dishes'))
