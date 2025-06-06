# Generated by Django 5.1.3 on 2024-12-29 11:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_rename_license_productitem_licenses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.CreateModel(
            name='ProductXLicense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('license', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.license')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.product')),
            ],
            options={
                'verbose_name_plural': 'Product X License',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='licenses',
            field=models.ManyToManyField(through='main.ProductXLicense', to='main.license'),
        ),
    ]
