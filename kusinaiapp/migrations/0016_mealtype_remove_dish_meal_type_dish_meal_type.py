# Generated by Django 5.0.7 on 2024-08-16 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kusinaiapp', '0015_alter_dish_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='dish',
            name='meal_type',
        ),
        migrations.AddField(
            model_name='dish',
            name='meal_type',
            field=models.ManyToManyField(to='kusinaiapp.mealtype'),
        ),
    ]
