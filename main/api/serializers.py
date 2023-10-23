from rest_framework import serializers

from main.models import Artwork, Artist
from django.conf import settings

from user.api.serializers import UserSerializer, UserReadOnlySerializer
from user.models import User


class ArtistSerializer(serializers.ModelSerializer):

    # nested field: nest user serializer into this (read-only by default)
    user = UserReadOnlySerializer(many=False, read_only=True)

    # show only specified slugfield (read-write by default but needs queryset)
    # user = serializers.SlugRelatedField(
    #     many=False,
    #     queryset=User.objects.all(),
    #     slug_field='username'
    # )

    # show only the __str__ field (read-only)
    # user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Artist
        fields = '__all__'
        extra_kwargs = {
            
        }


class ArtworkSerializer(serializers.ModelSerializer):

    # custom serializer field
    file_url = serializers.SerializerMethodField()

    # custom serializer field method to get property
    # syntax: get_<custom serializer field name>
    def get_file_url(self, object):
        return f"{settings.DOMAIN}/{object.file.resource.url}"

    # nested field: nest artist serializer into this
    artist = ArtistSerializer(many=False, read_only=True)

    class Meta:
        model = Artwork
        fields = '__all__'
        extra_kwargs = {
            'artist': {'read_only': True}
        }
