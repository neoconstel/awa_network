# Generated by Django 5.1.3 on 2024-12-04 01:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_alter_productcategory_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='root',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='branches', to='main.productcategory'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.productcategory'),
        ),
    ]
