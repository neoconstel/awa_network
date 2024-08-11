from django.shortcuts import render
from .models import Review

# for wagtail models LCRUD operations
from wagtail.admin.viewsets.model import ModelViewSet

from wagtail.admin.filters import WagtailFilterSet


class ReviewFilter(WagtailFilterSet):
    '''filterset_class for the ReviewViewset'''
    class Meta:
        model = Review
        fields = ['title', 'category', 'approved']

    '''
    ---set initial form values for this FilterSet---
    Syntax: data[<field_name>] = value
    ('approved') in this case is the field name of a radiobutton group of 3
    choices, each settable by the values: None, True and False respectively OR
    -1. 1 and 0 respectively.

    It works because this ReviewFilter class is a WagtailFilterSet, and
    WagtailFilterSets are built on top of the FilterSets from django-filter.

    Reference for this solution can be found here (comment from jcushman):
        https://github.com/carltongibson/django-filter/issues/322
    '''
    def __init__(self,data,*args,**kwargs):
        if not data.get('approved'):
            data = data.copy()
            data['approved'] = False
        super().__init__(data, *args, **kwargs)
        

# Create your views here.

# views for wagtail models LCRUD operations
class ReviewViewSet(ModelViewSet):
    model = Review
    form_fields = [
        "title", "content", "category", "tags", "caption_media_type",
        "caption_media_id", "body_media_type", "body_media_id", "approved"]
    icon = "openquote"
    add_to_admin_menu = True
    copy_view_enabled = False
    inspect_view_enabled = True
    menu_label = "Pending Reviews"

    # IMPORTANT addition. To provide a filter interface which we can customize
    # with default form values (default form values aren't a recommended
    # practice, but for now this is the most viable solution)
    filterset_class = ReviewFilter


review_viewset = ReviewViewSet("reviews")  # defines /admin/reviews/ as the base URL
