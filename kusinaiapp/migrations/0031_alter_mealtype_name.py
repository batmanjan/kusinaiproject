# Generated by Django 5.0.7 on 2024-10-21 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kusinaiapp', '0030_alter_mealtype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealtype',
            name='name',
            field=models.CharField(choices=[('Soup', 'Soup'), ('Pasta/Noodles', 'Pasta/Noodles'), ('Appetizer and Dessert', 'Appetizer and Dessert'), ('Vegetable Recipes', 'Vegetable Recipes'), ('Meat Recipes', 'Meat Recipes'), ('Seafood', 'Seafood')], max_length=50),
        ),
    ]
