# wagtail_hooks.py

from wagtail.admin.views.account import BaseSettingsPanel, SettingsTab
from wagtail import hooks
from .wagtail.forms import CustomSettingsForm

# for including custom css and javascript
from django.templatetags.static import static
from django.utils.safestring import mark_safe

custom_tab = SettingsTab('custom', "Custom settings", order=300)

@hooks.register('register_account_settings_panel')
class CustomSettingsPanel(BaseSettingsPanel):
    name = 'custom'
    title = "Other settings"
    # tab = custom_tab
    order = 100
    form_class = CustomSettingsForm
    form_object = 'user'
    template_name = 'user/admin/custom_settings.html'
    

# insert js globally to all admin pages
@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    """Add /static/js/custom.js to the admin."""
    return mark_safe(
        '<script defer src="{}"></script>'.format(static('/js/wagtail_custom_admin.js')),
    )
