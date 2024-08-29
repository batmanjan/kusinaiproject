from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    family_size = models.CharField(max_length=50, null=True, blank=True)
    age_range = models.JSONField(null=True, blank=True)
    meal_preference = models.JSONField(null=True, blank=True)
    allergies = models.JSONField(null=True, blank=True)
    cooking_skills = models.CharField(max_length=200, null=True, blank=True)
    survey_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class MealType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    dish_name = models.CharField(max_length=200)
    preparation_time = models.DurationField()
    ingredient_list = models.TextField()
    number_of_servings = models.CharField(max_length=50)
    procedure = models.TextField()
    nutritional_guide = models.TextField()
    skills_needed = models.CharField(max_length=200)
    age_range_that_can_eat = models.JSONField()
    cost = models.IntegerField()
    dish_image = models.ImageField(upload_to='dish_images/')
    meal_type = models.ManyToManyField(MealType)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.dish_name

class DishPlan(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    plan = models.CharField(max_length=100)
    saved_date = models.DateField(null=True, blank=True)  # Add this line

    class Meta:
        unique_together = ('user', 'dish')
class CookedDish(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'dish')
