# Generated by Django 4.2.7 on 2024-05-16 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0026_reactiontype_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='artwork',
            name='unique_content_object',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='views',
        ),
        migrations.AddConstraint(
            model_name='artwork',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id'), name='unique_artwork'),
        ),
        migrations.AddConstraint(
            model_name='reaction',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id', 'user', 'reaction_type'), name='unique_reaction'),
        ),
        migrations.AddField(
            model_name='viewlog',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='viewlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='viewlog',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id', 'user'), name='unique_view'),
        ),
    ]
