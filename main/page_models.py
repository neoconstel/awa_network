from .models import *

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField

from wagtail.search import index


class BasePage(Page):
    is_creatable = False # List Page type in admin? (not inherited)


class HomePage(BasePage):
    parent_page_types = ['wagtailcore.Page']

    # body = models.TextField(help_text='blablabla', blank=True)

    # content_panels = Page.content_panels + [
    #     FieldPanel('body'),
    # ]

    # # To show custom fields in the API results, the fields must be included in 
    # # api_fields and then also included in the urlparams, as shown:
    # # http://127.0.0.1:8000/api/v2/pages/?type=blog.BlogPage&fields=intro,body
    # api_fields = [
    #     APIField('body')
    # ]

    # search_fields = Page.search_fields + [
    #     index.SearchField('body')
    # ]


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
    