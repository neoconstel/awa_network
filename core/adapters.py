from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This method is called after successful authentication from the provider
        but before the login is actually processed.
        """
        # If social account is already linked, no need to do anything
        if sociallogin.is_existing:
            return

        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            # Try to find an existing user with that email
            user = User.objects.get(email=email)
            # Link this new social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass  # Let Allauth proceed with normal signup
