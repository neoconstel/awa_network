from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .models import User

from wagtail.users.forms import UserEditForm, UserCreationForm


def is_valid_email(email):
    '''Checks email validity using RFC 5322 compliant regex standard'''
    pattern = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"
    return bool(re.match(pattern, email))

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
    username = forms.CharField(required=False, label=_("Username"))
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


    # override this method to override the default buggy validators which
    # are as a result of using a custom User model
    # e.g 'email' validator saying 'username' already exists when username
    # field is blank
    def clean(self):
        pass


    # custom validators (to replace overridden functionalities)

    def clean_email(self):
        '''
        validations:
        - must not be empty (handled by the 'required' setting)
        - must match email regex
        - must not already belong to existing user
        '''
        email = self.cleaned_data["email"]

        if not is_valid_email(email):
            raise ValidationError("Enter a valid email address!!!.")

        if User.objects.filter(email=email).first():
            raise ValidationError("User with this email already exists!!!.")        

        return email

    def clean_username(self):
        '''
        validations:
        - must not be empty (handled by the 'required' setting)
        - must not already belong to existing user
        '''
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).first():
            raise ValidationError("User with this username already exists!!!.")        
            
        return username

        