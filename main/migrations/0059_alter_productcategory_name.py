# Generated by Django 5.1.3 on 2024-12-15 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_remove_product_user_ratings_productrating_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
