# Generated by Django 5.0.7 on 2024-08-27 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kusinaiapp', '0021_remove_cookeddish_cooked_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='dishplan',
            name='saved_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
