from django import forms
from wagtail.admin.forms import WagtailAdminPageForm
from django.core.exceptions import ValidationError
from .models import Artwork


# custom form for the HomePage model
class HomePageForm(WagtailAdminPageForm):
    '''The Page model which this form gets attached to (via the
    'base_form_class' attribute) will automatically have its fields processed 
    by this form. Extra fields can be added to the form. For instance:    
    
    address = forms.CharField()

    Any extra fields must also be added to the page's field_panels in order to
    have its fields visible for editing (as with the page's default fields).
    '''

    # validate specific field (syntax: clean_<field name>)
    # def clean_spotlight_art_ID(self):
    #     spotlight_art_ID = self.cleaned_data['spotlight_art_ID']
    #     if spotlight_art_ID < 1:
    #         raise ValidationError('spotlight art ID must be >= 1!')


    # validate one or more fields
    def clean(self):
        # the default validations (for every field)
        cleaned_data = super().clean()

        # extra custom validation logic
        spotlight_art_ID = cleaned_data['spotlight_art_ID']
        if spotlight_art_ID != None:
            if not isinstance(spotlight_art_ID, int):
                self.add_error(
                    'spotlight_art_ID', 'spotlight_art_ID must be a valid integer!')

            else:
                if not Artwork.objects.filter(id=spotlight_art_ID).first():
                    self.add_error('spotlight_art_ID', f"The ID:\
                            {spotlight_art_ID} doesn't belong to any artwork!")

        return cleaned_data

    def save(self, commit=True):
        page = super().save(commit=False)

        # logic of everything to be done before final save


        if commit:
            page.save()
        return page
