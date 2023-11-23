from django.db import models
from django.utils import timezone
import time
import random

from django.contrib.auth import get_user_model
User = get_user_model()

# Generic Foreign Key Relationships
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.
class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='artist')
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"Artist{self.id} | {self.user.username}"


class ArtCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"ArtCategory{self.id} | {self.name}"


class FileType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"FileType{self.id} | {self.name}"


class FileGroup(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"FileGroup{self.id} | {self.name}"


class Artwork(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='artworks')
    # file = models.OneToOneField(
    #     File, on_delete=models.CASCADE, related_name='artwork')
    category = models.ForeignKey(ArtCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=200, blank=True, null=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    # TODO: validate that there actually exists an object with content_type
    # and object_id
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()

    # can be File or Image    
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        constraints = [
            # no instance should have the same content_type and object_id
            models.UniqueConstraint(
                fields=['content_type', 'object_id'], name='unique_content_object')
        ]

    def __str__(self):
        return f"Artwork{self.id} | {self.title}"


class File(models.Model):
    def save_path(instance, filename):
        '''
        instance: the File instance
        filename: the original name of the resource e.g "Itachi.png"
        '''

        # file will be uploaded to MEDIA_ROOT/media_group/media_type/filename
        # e.g /media/artworks/images/Itachi.png
        return (
            f'{instance.file_group.name}/'            
            f'{instance.file_type.name}/{random.randint(1000000, 9999999)}'
            f'_{time.strftime("%b-%d-%Y__%H-%M-%S__%z")}'
            f'_{filename}'
        )

    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    file_group = models.ForeignKey(FileGroup, on_delete=models.CASCADE)
    resource = models.FileField(upload_to=save_path)
    upload_date = models.DateTimeField(default=timezone.now)

    # generic related fields for reverse quering
    artwork = GenericRelation(Artwork, related_query_name='file_object')

    def __str__(self):
        return f"File{self.id} | {self.resource.name}"


class Image(models.Model):
    # TODO: save_path method for both Image and File should be defined outside
    def save_path(instance, filename):
        '''
        instance: the Image instance
        filename: the original name of the resource e.g "Itachi.png"
        '''

        # image will be uploaded to MEDIA_ROOT/media_group/image/filename
        # e.g /media/artworks/image/Itachi.png
        return (
            f'{instance.file_group.name}/'            
            f'image/{random.randint(1000000, 9999999)}'
            f'_{time.strftime("%b-%d-%Y__%H-%M-%S__%z")}'
            f'_{filename}'
        )

    file_group = models.ForeignKey(FileGroup, on_delete=models.CASCADE)
    resource = models.ImageField(upload_to=save_path)
    upload_date = models.DateTimeField(default=timezone.now)

    # generic related fields for reverse quering
    artwork = GenericRelation(Artwork, related_query_name='image_object')

    def __str__(self):
        return f"Image{self.id} | {self.resource.name}"


class Following(models.Model):
    follower = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"Following{self.id}: {self.follower} -> {self.following}"


# execute this part only from models.py in the 'main' app
if __name__ == 'main.models':
    # import wagtail page models
    from .page_models import *