from django.contrib import admin
from .models import User, InvalidAccessToken


class UserAdmin(admin.ModelAdmin):
    '''Control what happens when the User model is saved FROM the admin panel.
    Use set_password (encrypt) only if user object is newly created or password
    has been changed. This ensures that the new password (plain text) is stored
    as a hash, and that the existing password hash doesn't get re-encrypted by 
    accident -- which would cause an unintended password mismatch.'''
    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(InvalidAccessToken)
