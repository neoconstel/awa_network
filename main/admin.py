from django.contrib import admin
from .models import (Artist, FileType, File, Artwork, Following, ArtCategory,
FileGroup, Image, ReactionType, Reaction, ViewLog, Comment, Review, Genre,
ArticleCategory, Article, Seller, ProductCategory, License,
ProductRating, Product, ProductXImage, ProductItem, ProductItemXLicense,
ProductXLicense)

# filepond
from django_drf_filepond.models import TemporaryUpload

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
admin.site.register(Genre)
admin.site.register(ArticleCategory)
admin.site.register(Article)
admin.site.register(Seller)
admin.site.register(ProductCategory)
admin.site.register(License)
admin.site.register(ProductRating)
admin.site.register(Product)
admin.site.register(ProductXImage)
admin.site.register(ProductItem)
admin.site.register(ProductItemXLicense)
admin.site.register(ProductXLicense)
admin.site.register(TemporaryUpload)

# wagtail
admin.site.register(Page)
