'''TODO:
    - convert all Interger primary keys to BigInteger fields (UUID where possible)
'''


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
class ReactionType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"ReactionType{self.id}: {self.name}"


class Reaction(models.Model):
    reaction_type = models.ForeignKey(ReactionType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # generic relationship fields -- can react on post, comment, etc
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    class Meta:
        constraints = [
            # no instance should have the same content_type, object_id, user
            # and reaction_type
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'user', 'reaction_type'],
                name='unique_reaction')
        ]


    def __str__(self):
        return f"Reaction{self.id}: {self.reaction_type.name} | Object: {self.content_object} | User:{self.user.username}"


class Comment(models.Model):
    '''A post in this context could be an artwork upload, a review, a challenge
    submission, an announcement, a song, etc. These can all have their
    individual models (like the Artwork model), so this comment model is a
    generic model meant to reference a post from any model. I have customized
    the content_type and object_id field names to make it easier to understand
    the working of the Comment model.'''

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    # generic post type -- can comment on any model instance
    post_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    post_id = models.IntegerField()
    post_object = GenericForeignKey('post_type', 'post_id')

    content = models.TextField(null=False)
    parent_comment = models.ForeignKey('self', null=True, blank=True,
                    on_delete=models.CASCADE, related_name='child_comments')    
    date_posted = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        parent_id = str(self.parent_comment.id) if self.parent_comment else ""
        parent_string = f"<parent: {parent_id}>" if parent_id else ""
        return f"Comment{self.id}{parent_string}: [{self.content}] by <{self.user.username}> on {self.post_object}"


class ViewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # generic relationship fields -- can view post, comment, etc
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    class Meta:
        constraints = [
            # no instance should have the same content_type, object_id, user
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'user'],
                name='unique_view')
        ]


    def __str__(self):
        return f"ViewLog{self.id}: | Object: {self.content_object} | User:{self.user.username}"


class Artist(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='artist')
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    bio = models.CharField(max_length=100, blank=True, null=True)
    tools = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Artist{self.id} | {self.user.username}"


class ArtCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"ArtCategory{self.id} | {self.name}"


class FileType(models.Model):
    '''e.g image, video, sound, 3D, project, document, web, other'''
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"FileType{self.id} | {self.name}"


class FileGroup(models.Model):
    '''e.g site_content, user_profile, artist_profile, artworks, 
                reviews, articles'''
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
    description = models.CharField(max_length=1000, blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)
    date_published = models.DateTimeField(default=timezone.now)

    # TODO: validate that there actually exists an object with content_type
    # and object_id
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()

    # can be File or Image    
    content_object = GenericForeignKey('content_type', 'object_id')

    '''generic related fields for reverse quering (many to many behaviour)
    note that in the case of <comments>, which is of the Comment model (where
    a custom content_type/object_id field name has been used, we now specify)
    the custom field names (for the COMMENT model) in the GenericRelation
    we are creating in the Artwork model'''
    reactions = GenericRelation(Reaction, related_query_name='reaction_artwork_object')
    views = GenericRelation(ViewLog, related_query_name='viewlog_artwork_object')
    comments = GenericRelation(Comment, related_query_name='comment_artwork_object',
                    content_type_field='post_type', object_id_field='post_id')


    class Meta:
        constraints = [
            # no instance should have the same content_type and object_id
            models.UniqueConstraint(
                fields=['content_type', 'object_id'], name='unique_artwork')
        ]

    def __str__(self):
        return f"Artwork{self.id} ({self.title})"


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
    

class Genre(models.Model):
    '''this model was created with Reviews in mind, so that a review of even a
    non-art subject such as a movie could have a genre. E.g Horror.'''

    name = models.CharField(max_length=50)

    @classmethod
    def get_default_pk(cls):
        '''for Review model (and any other model referencing Genre via foreign
        key) to get a default pk with which to point to Genre'''
        genre, created = cls.objects.get_or_create(
            name='Unclassified'
        )
        return genre.pk

    def __str__(self):
        return f"Genre{self.id} | {self.name}"


class Review(models.Model):    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=10000)
    category = models.ForeignKey(ArtCategory, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)
    genre = models.ForeignKey(Genre, default=Genre.get_default_pk, 
                              on_delete=models.CASCADE)
    tags = models.CharField(max_length=200, blank=True, null=True)
    date_published = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    # TODO: validate that there actually exists an object with caption_media_type
    # and caption_media_object
    caption_media_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="+")
    caption_media_id = models.IntegerField()
    caption_media_object = GenericForeignKey('caption_media_type', 'caption_media_id')

    body_media_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    body_media_id = models.IntegerField(blank=True, null=True)
    body_media_object = GenericForeignKey('body_media_type', 'body_media_id')


    '''generic related fields for reverse quering (many to many behaviour)
    note that the content_type_field and object_id_field belong to the COMMENT
    model, NOT this Review model'''
    comments = GenericRelation(Comment, related_query_name='comment_review_object',
                    content_type_field='post_type', object_id_field='post_id')

    def __str__(self):
        return f"Review{self.id} ({self.title})"
    

class ArticleCategory(models.Model):
    '''e.g art skills, career, inspiration, news, ads, challenges, updates'''
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"ArticleCategory{self.id} | {self.name}"

    
class Article(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
                             related_name='articles')
    title = models.CharField(max_length=100)
    categories = models.CharField(max_length=100)
    tags = models.CharField(max_length=200, blank=True, null=True)
    date_published = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    html_file = models.ForeignKey(
                        File, on_delete=models.CASCADE)
    html_images = models.JSONField(default=dict)
    thumbnail_image = models.ForeignKey(Image, null=True,
                                        on_delete=models.SET_NULL)

    def __str__(self):
        return f"Article{self.id} ({self.title})"



# execute this part only from models.py in the 'main' app
if __name__ == 'main.models':
    # import wagtail page models
    from .page_models import *