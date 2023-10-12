# inbuilt django signals
from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

# custom signals
import django.dispatch
new_following = django.dispatch.Signal()

# decorator for receiving signals
from django.dispatch import receiver

# models
from .models import User, Artist, Artwork
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
    
    # delete attached file instance and the resource it points to
    model_instance.file.resource.delete()
    model_instance.file.delete()

    # print(f'\n\n\nEXECUTED SIGNAL:  artwork and file deleted\n\n\n')
    
        