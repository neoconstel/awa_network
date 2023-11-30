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
    parent_page_types = ['wagtailcore.Page']

    # custom form to be used when creating/editing page in admin
    base_form_class = HomePageForm

    # body = models.TextField(help_text='blablabla', blank=True)

    # this should be validated on page publish to ensure valid artwork id
    spotlight_art = models.IntegerField(
        help_text='ID of the Spotlight Art', blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('spotlight_art'),
        InlinePanel('sliding_images', label="Sliding images"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('spotlight_art'),
    ]

    # To show custom fields in the API results, the fields must be included in 
    # api_fields and then also included in the urlparams, as shown:
    # http://localhost:8000/api/v2/pages/?type=main.HomePage&fields=intro,body
    api_fields = [
        APIField('sliding_images')
    ]

    # search_fields = Page.search_fields + [
    #     index.SearchField('body')
    # ]


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
    