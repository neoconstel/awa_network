from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

# enter fields from the custom user model which should be displayed in
# wagtail user create/user edit forms. The "membership" field of the custom
# user model is used as an example.

class CustomUserEditForm(UserEditForm):
    username = forms.CharField(required=True, label=_("Username"))
    gender = forms.CharField(required=False, label=_("Gender"))
    membership = forms.CharField(required=False, label=_("Membership"))
    bio = forms.CharField(required=False, label=_("Bio"))
    is_staff = forms.BooleanField(required=False, label=_("Is Staff"))
    is_active = forms.BooleanField(required=False, label=_("Is Active"))
    is_verified = forms.BooleanField(required=False, label=_("Is Verified"))
    profile_image = forms.ImageField(required=False, label=_("Profile Image"))


    def save(self, *args, **kwargs):
        # set the user email to the value of the form's email field. By
        # default, it unexpectedly sets the user email to the value of the
        # username (i.e self.instance.email = self.instance.username)
        self.instance.email = self.cleaned_data.get('email')

        return super().save(*args, **kwargs)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(required=True, label=_("Username"))
    gender = forms.CharField(required=False, label=_("Gender"))
    membership = forms.CharField(required=False, label=_("Membership"))
    bio = forms.CharField(required=False, label=_("Bio"))
    is_staff = forms.BooleanField(required=False, label=_("Is Staff"))
    is_active = forms.BooleanField(required=False, label=_("Is Active"))
    is_verified = forms.BooleanField(required=False, label=_("Is Verified"))
    profile_image = forms.ImageField(required=False, label=_("Profile Image"))

    def save(self, *args, **kwargs):
        # set the user email to the value of the form's email field. By
        # default, it unexpectedly sets the user email to the value of the
        # username (i.e self.instance.email = self.instance.username)
        self.instance.email = self.cleaned_data.get('email')
        
        return super().save(*args, **kwargs)
        