# Generated by Django 5.0.7 on 2024-08-29 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kusinaiapp', '0023_alter_dishplan_saved_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChefAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
    ]