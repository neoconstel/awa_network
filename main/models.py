from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()


# Create your models here.
class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='artist_instance')
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
        return f'{instance.file_type.name}/{filename}'

    name = models.CharField(max_length=100)
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    resource = models.FileField(upload_to=user_directory_path)

    def __str__(self):
        return f"File{self.id} | {self.name} | {self.file_type.name}"


class Artwork(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    file = models.OneToOneField(
        File, on_delete=models.CASCADE, related_name='artwork')
    category = models.ForeignKey(ArtCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=200)
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
        