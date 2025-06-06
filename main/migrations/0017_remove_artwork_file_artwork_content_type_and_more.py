# Generated by Django 4.2.7 on 2023-11-23 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0016_alter_image_resource'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artwork',
            name='file',
        ),
        migrations.AddField(
            model_name='artwork',
            name='content_type',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='artwork',
            name='object_id',
            field=models.PositiveBigIntegerField(default=1),
            preserve_default=False,
        ),
    ]
