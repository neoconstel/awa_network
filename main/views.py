from django.shortcuts import render
from .models import Review

# for wagtail models LCRUD operations
from wagtail.admin.viewsets.model import ModelViewSet

from wagtail.admin.filters import WagtailFilterSet


class ReviewFilter(WagtailFilterSet):
    class Meta:
        model = Review
        fields = ['approved']
        

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

    filterset_class = ReviewFilter


review_viewset = ReviewViewSet("reviews")  # defines /admin/reviews/ as the base URL
