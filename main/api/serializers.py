from rest_framework import serializers

from main.models import Artwork


class ArtworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artwork
        fields = '__all__'
        extra_kwargs = {
            'artist': {'read_only': True},
            'file': {'read_only': True},
        }
