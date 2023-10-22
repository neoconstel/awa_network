from rest_framework import serializers

from main.models import Artwork
from django.conf import settings


class ArtworkSerializer(serializers.ModelSerializer):

    # custom serializer field
    file_url = serializers.SerializerMethodField()

    # custom serializer field method to get property
    # syntax: get_<custom serializer field name>
    def get_file_url(self, object):
        return f"{settings.DOMAIN}/{object.file.resource.url}"

    class Meta:
        model = Artwork
        fields = '__all__'
        extra_kwargs = {
            'artist': {'read_only': True}
        }
