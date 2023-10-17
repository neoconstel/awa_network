# import-export
from import_export import resources
from import_export.fields import Field


# models
from .models import Artwork


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


import json
class ArtCategoryResource(resources.ModelResource):    
    class Meta:
        model = Artwork

    def export_data():
        dataset = ArtCategoryResource().export()
        data = []
        for obj in dataset:
            data.append({
                "model": "myapp.mymodel",
                "fields": obj
            })
        return json.dumps(data)