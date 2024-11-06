# inbuilt django signals
from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

# custom signals
import django.dispatch
new_following = django.dispatch.Signal()

# decorator for receiving signals
from django.dispatch import receiver

# models
from .models import User, Artist, Artwork, File, Image, Review
from django.contrib.contenttypes.models import ContentType




# ----EXAMPLE----
# <sender> points to the model to listen to. None by default, meaning it listens to all.
@receiver(request_finished, sender=None, dispatch_uid='unique-string-to-protect-against-duplicate-signal')
def my_callback(sender, **kwargs):
    pass
    # print(f'\n\n\nEXECUTED SIGNAL:  Request Finished!!!\n\n\n')


# -------USER-------
@receiver(post_save, sender=User, dispatch_uid='user-uid')
def user_listener(sender, **kwargs):
    model_instance = kwargs.get('instance')
    newly_created = kwargs.get('created')

    # only create an artist instance IF this instance is newly created
    if newly_created:
        # create artist for this user
        artist = Artist(
            user=model_instance
        )
        artist.save()

        # print(f'\n\n\nEXECUTED SIGNAL:  artist created\n\n\n')


# -------Artwork-------
@receiver(post_delete, sender=Artwork, dispatch_uid='artwork-uid')
def artwork_listener(sender, **kwargs):
    model_instance = kwargs.get('instance')
    
    # delete attached file instance (file or image object as per generic field)
    # model_instance.file.delete()
    content_object = model_instance.content_type.model_class().objects.get(
        id=model_instance.object_id)
    content_object.delete()

    # print(f'\n\n\nEXECUTED SIGNAL:  artwork deleted\n\n\n')


# -------File-------
@receiver(pre_delete, sender=File, dispatch_uid='file-uid')
def file_listener(sender, **kwargs):
    model_instance = kwargs.get('instance')
    
    # delete the resource it points to
    model_instance.resource.delete()

    # print(f'\n\n\nEXECUTED SIGNAL:  file and attached resource deleted\n\n\n')


# -------Image-------
@receiver(pre_delete, sender=Image, dispatch_uid='image-uid')
def image_listener(sender, **kwargs):
    model_instance = kwargs.get('instance')
    
    # delete the resource it points to
    model_instance.resource.delete()

    # print(f'\n\n\nEXECUTED SIGNAL:  image and attached resource deleted\n\n\n')


# -------Review-------
@receiver(post_delete, sender=Review, dispatch_uid='review-uid')
def review_listener(sender, **kwargs):
    model_instance = kwargs.get('instance')
    
    # delete attached file instance (file or image object as per generic field)
    # model_instance.file.delete()
    caption_media_object = \
        model_instance.caption_media_type.model_class().objects.get(
        id=model_instance.caption_media_id)
    caption_media_object.delete()

    # delete optionally-attached file instance (file or image object as per generic field)
    # model_instance.file.delete()
    # if it has a body media, then proceed
    if model_instance.body_media_id:
        body_media_object = \
            model_instance.body_media_type.model_class().objects.get(
            id=model_instance.body_media_id)
        body_media_object.delete()

    # print(f'\n\n\nEXECUTED SIGNAL:  review deleted\n\n\n')
