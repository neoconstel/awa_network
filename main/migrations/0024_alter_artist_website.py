# Generated by Django 4.2.7 on 2024-04-30 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_artist_bio_artist_location_artist_tools_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='website',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
