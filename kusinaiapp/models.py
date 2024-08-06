from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Provided from signup and survey
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    family_size = models.CharField(max_length=50, null=True, blank=True)
    age_range = models.JSONField(null=True, blank=True)
    meal_preference = models.JSONField(null=True, blank=True)
    allergies = models.JSONField(null=True, blank=True)  # No default value
    cooking_skills = models.CharField(max_length=200, null=True, blank=True)
    survey_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.username




class Dish(models.Model):
    MEAL_TYPE_CHOICES = [
        ('Appetizer', 'Appetizer'),
        ('Soup', 'Soup'),
        ('Dessert', 'Dessert'),
        ('Vegetable Dishes', 'Vegetable Dishes'),
        ('Vegetable with Seafood', 'Vegetable with Seafood'),
        ('Vegetable with Meat', 'Vegetable with Meat'),
    ]
    
    COST_CHOICES = [
        ('100-200', '100-200'),
        ('300-400', '300-400'),
        ('500-600', '500-600'),
        ('700-800', '700-800'),
        ('900-1000', '900-1000'),
    ]
    
    dish_name = models.CharField(max_length=200)
    preparation_time = models.DurationField()
    ingredient_list = models.TextField()  # Changed to TextField for multiple values
    number_of_servings = models.CharField(max_length=50)  # Changed to CharField for ranges
    procedure = models.TextField()
    nutritional_guide = models.TextField()
    skills_needed = models.CharField(max_length=200)
    age_range_that_can_eat = models.JSONField()  # JSON field for multiple values
    cost = models.CharField(max_length=20, choices=COST_CHOICES)  # Changed to CharField with choices
    dish_image = models.ImageField(upload_to='dish_images/')
    meal_type = models.CharField(max_length=30, choices=MEAL_TYPE_CHOICES)  

    def __str__(self):
        return self.dish_name



# Provided from saving dish from home to saved page
class DishPlan(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    plan = models.CharField(max_length=100)  # Adjust field type as needed
    

    class Meta:
        unique_together = ('user', 'dish')  # Ensure unique plans per user and dish
        
class CookedDish(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    cooked_date = models.DateTimeField(auto_now_add=True)  # Track when the dish was cooked
    rating = models.IntegerField(null=True, blank=True)  # Add this line if not already present

    class Meta:
        unique_together = ('user', 'dish')  # Ensure unique cooked dishes per user

