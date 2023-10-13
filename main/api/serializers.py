from rest_framework import serializers

from main.models import Artwork, ArtCategory


class ArtworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artwork
        fields = '__all__'
        extra_kwargs = {
            'artist': {'read_only': True},
            'file': {'read_only': True},
        }


    def save(self, **kwargs):
        
        artwork = Artwork(**self.validated_data)
        return artwork


class ArtCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtCategory
        fields = '__all__'
        extra_kwargs = {
            
        }
        