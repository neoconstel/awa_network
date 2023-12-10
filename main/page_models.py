from django.db import models
from .models import Artwork
from .page_forms import HomePageForm

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField

from modelcluster.fields import ParentalKey

from wagtail.search import index

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class BasePage(Page):
    is_creatable = False # List Page type in admin? (not inherited)


class HomePage(BasePage):
    '''
    custom API fields:
    - gallery_images
    - spotlight_art
    '''
    parent_page_types = ['wagtailcore.Page']

    # custom form to be used when creating/editing page in admin
    base_form_class = HomePageForm

    # body = models.TextField(help_text='blablabla', blank=True)

    spotlight_art_caption = models.CharField(max_length=100, blank=True, null=True)

    # this should be validated on page publish to ensure valid artwork id
    spotlight_art_ID = models.IntegerField(
        help_text='ID of the Spotlight Art (you can find it in its url)', blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('spotlight_art_ID'),
        FieldPanel('spotlight_art_caption'),
        InlinePanel('sliding_images', label="Sliding images"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('spotlight_art_ID'),
    ]

    # To show custom fields in the API results, the fields must be included in 
    # api_fields and then also included in the urlparams, as shown:
    # http://localhost:8000/api/v2/pages/?type=main.HomePage&fields=intro,body
    api_fields = [
        APIField('gallery_images'),
        APIField('spotlight_art'),
        APIField('spotlight_caption'),
    ]

    # search_fields = Page.search_fields + [
    #     index.SearchField('body')
    # ]

    # custom API field
    @property
    def gallery_images(self):

        # in a normal page object, this would be 'self.homepage'
        # but because this model inherited from 'basepage', so we have
        # 'self.basepage.homepage' instead
        gallery_image_list = self.basepage.homepage.sliding_images.all()

        gallery_objects = []
        for gallery_image in gallery_image_list:
            gallery_object = {
                'url': gallery_image.image.file.url,
                'caption': gallery_image.caption
            }
            gallery_objects.append(gallery_object)

        return gallery_objects


    @property
    def spotlight_art(self):
        id = self.basepage.homepage.spotlight_art_ID
        url = Artwork.objects.get(id=id).image_object.first().resource.url
        artwork = {
            'id': id,
            'image_url': url
        }
        return artwork

    
    @property
    def spotlight_caption(self):
        return self.basepage.homepage.spotlight_art_caption


class HomePageSlidingImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='sliding_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]


class SpotlightPage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class TvPage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class ReviewsPage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class ChallengePage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class MagazinePage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class FoundationPage(BasePage):
    parent_page_types = ['main.HomePage']
    max_count = 1


class AnimationChallengePage(BasePage):
    parent_page_types = ['main.ChallengePage']


class ConceptChallengePage(BasePage):
    parent_page_types = ['main.ChallengePage']
    
