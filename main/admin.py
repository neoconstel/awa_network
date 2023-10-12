from django.contrib import admin
from .models import Artist, FileType, File, Artwork, Following, ArtCategory

# Register your models here.
admin.site.register(Artist)
admin.site.register(ArtCategory)
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(Artwork)
admin.site.register(Following)
