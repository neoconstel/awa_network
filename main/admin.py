from django.contrib import admin
from .models import Artist, FileType, File, Artwork, Following, ArtCategory

from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field 


# import-export setup
class ArtworkResource(resources.ModelResource):
    '''fields: the fields of the model to import/export. Not specifying fields
    exports all of them by default.'''
    
    # for using optional features such as dehydrate_<fieldname>()
    artist = Field()
    
    class Meta:
        model = Artwork
        # fields = ('id', 'artist', 'file', 'category', 'title', 'tags', 'views', 'likes')
        # export_order = fields


    # Define how a specific field gets exported (optional). e.g instead of exporting 
    # artwork.artist.pk by default, export artwork.artist.user.username instead.
    # syntax: dehydrate_<field name>.'''
    # def dehydrate_artist(self, obj):
    #     return obj.artist.user.username

class ArtworkAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class=ArtworkResource


# Register your models here.
admin.site.register(Artist)
admin.site.register(ArtCategory)
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(Following)
