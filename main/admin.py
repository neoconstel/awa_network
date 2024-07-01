from django.contrib import admin
from .models import (Artist, FileType, File, Artwork, Following, ArtCategory,
FileGroup, Image, ReactionType, Reaction, ViewLog, Comment, Review)

# wagtail
from .models import Page

from import_export.admin import ExportActionMixin

# import your resource classes
from .resources import ArtworkResource, ArtCategoryResource


class ArtworkAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class=ArtworkResource

class ArtCategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class=ArtCategoryResource


# Register your models here.
admin.site.register(Artist)
admin.site.register(ArtCategory, ArtCategoryAdmin)
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(Following)
admin.site.register(FileGroup)
admin.site.register(Image)
admin.site.register(ReactionType)
admin.site.register(Reaction)
admin.site.register(ViewLog)
admin.site.register(Comment)
admin.site.register(Review)


# wagtail
admin.site.register(Page)
