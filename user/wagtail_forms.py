from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

# enter fields from the custom user model which should be displayed in
# wagtail user create/user edit forms. The "membership" field of the custom
# user model is used as an example.

class CustomUserEditForm(UserEditForm):
    membership = forms.CharField(required=False, label=_("Membership"))


class CustomUserCreationForm(UserCreationForm):
    membership = forms.CharField(required=False, label=_("Membership"))
