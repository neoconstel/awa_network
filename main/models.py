from django.db import models
from django.utils import timezone
import time
import random

from django.contrib.auth import get_user_model
User = get_user_model()


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


class File(models.Model):
    def user_directory_path(instance, filename):
        '''
        instance: the File instance
        filename: the original name of the resource e.g "Itachi.png"
        '''

        # file will be uploaded to MEDIA_ROOT/media_type/filename
        # e.g /media/images/Itachi.png
        return (            
            f'{instance.file_type.name}/{random.randint(1000000, 9999999)}'
            f'_{time.strftime("%b-%d-%Y__%H-%M-%S__%z")}'
            f'_{filename}'
        )

    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    resource = models.FileField(upload_to=user_directory_path)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"File{self.id} | {self.resource.name}"


class Artwork(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='artworks')
    file = models.OneToOneField(
        File, on_delete=models.CASCADE, related_name='artwork')
    category = models.ForeignKey(ArtCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=200, blank=True, null=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"Artwork{self.id} | {self.title}"


class Following(models.Model):

    follower = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"Following{self.id}: {self.follower} -> {self.following}"


class SpotlightArt(models.Model):
    artwork = models.OneToOneField(Artwork, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"SpotlightArt{self.id} | {self.artwork.title}"

    def save(self, *args, **kwargs):
        # if trying to save new instance and an instance already exists, abort
        if (not self.pk) and self.__class__.objects.count():
            print("Only one instance of SpotlightArt is allowed. Save aborted")
        else:
            super().save(*args, **kwargs)
            


# class CarouselAsset(models.Model):
#     # instances with same carousel_group belong to the same carousel
#     carousel_group = models.IntegerField(default=1)
#     position = models.IntegerField(default=1) # sorted carousel position
#     file = models.OneToOneField(
#         File, on_delete=models.CASCADE, related_name='carousel_asset')
