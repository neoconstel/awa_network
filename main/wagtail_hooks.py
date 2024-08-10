# wagtail_hooks.py

from wagtail import hooks
from .views import review_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return review_viewset
