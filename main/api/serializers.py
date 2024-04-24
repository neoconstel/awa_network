from rest_framework import serializers

from main.models import Artwork, Artist, ArtCategory, Following
from django.conf import settings

from user.api.serializers import UserReadOnlySerializer


class ArtistSerializer(serializers.ModelSerializer):

    # nested field: nest user serializer into this (read-only by default)
    # -------different ways of implementation---------
    user = UserReadOnlySerializer(many=False, read_only=True)

    # show only specified slugfield (read-write by default but needs queryset)
    # user = serializers.SlugRelatedField(
    #     many=False,
    #     queryset=User.objects.all(),
    #     slug_field='username'
    # )

    # show only the __str__ field (read-only)
    # user = serializers.StringRelatedField(many=False)
    #-------------------------------------------------------------

    # custom serializer fields
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    # methods to get the custom fields (syntax: get_<custom serializer field>)
    def get_followers(self, object):
        return object.followers.count()

    def get_following(self, object):
        return object.following.count()

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
        '''this method returns an OrderedDict during the Artwork creation,
        as it isn't yet a valid object. Just data. And no url to be returned
        yet. Hence this try block'''
        try:
            object.pk # object has id.
        except:
            return ""
        else:
            return f"{object.content_object.resource.url}"

    # nested field: nest artist serializer into this
    artist = ArtistSerializer(many=False, read_only=True)

    class Meta:
        model = Artwork
        fields = '__all__'

        # content_type/object_id are set False because at POST (creation of
        # Artwork instance, there isn't yet a file content_type/object_id)
        extra_kwargs = {
            'artist': {'read_only': True},
            'content_type': {'required': False},
            'object_id': {'required': False}
        }

    def validate(self, data):
        super().validate(data)

        content_type = data.get('content_type')
        object_id = data.get('object_id')

        if content_type and object_id:
            #TODO: also implement unique together constraint
            try:
                content_type.get_object_for_this_type(id=object_id)
            except:
                raise serializers.ValidationError(
                    "object_id invalid for content_type!")

        elif content_type:
            raise serializers.ValidationError("content_type needs object_id!")

        elif object_id:
            raise serializers.ValidationError("object_id needs content_type!")

        
        return data


class ArtCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtCategory
        fields = '__all__'
        extra_kwargs = {
            
        }


class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Following
        fields = '__all__'
        extra_kwargs = {
            
        }
        