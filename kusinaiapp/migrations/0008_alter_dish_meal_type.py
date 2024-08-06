# Generated by Django 5.0.7 on 2024-08-04 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kusinaiapp', '0007_dish_meal_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='meal_type',
            field=models.CharField(choices=[('Appetizer', 'Appetizer'), ('Soup', 'Soup'), ('Dessert', 'Dessert'), ('Vegetable Dishes', 'Vegetable Dishes'), ('Vegetable with Seafood', 'Vegetable with Seafood'), ('Vegetable with Meat', 'Vegetable with Meat')], max_length=30),
        ),
    ]
