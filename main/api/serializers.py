from rest_framework import serializers
import re

# models
from main.models import (Artwork, Artist, ArtCategory, Following, Reaction,
ViewLog, Comment, Review, ArticleCategory, Article, Product, Seller,
ProductCategory, ProductRating, ProductItem, License, ProductXLicense,
Contest)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# imported serializers
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
    views = serializers.SerializerMethodField()

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


    def get_views(self, object):
        # return default value if the artwork instance is being created
        if not 'id' in dir(object):
            return 0

        art_type = ContentType.objects.get_for_model(Artwork)
        view_logs = ViewLog.objects.filter(content_type=art_type,object_id=object.id)
        return view_logs.count()


    class Meta:
        model = Artwork
        fields = '__all__'

        '''I exclude content_type and object_id because they remain 'required'
        even after setting 'required' to False in extra_kwargs. Even though
        excluded, they are still writable but not visible in JSON output.

        To view them in the output, I then create SerializerMethodFields with
        similar field names just to expose them in the output.
        '''
        # exclude = ['content_type', 'object_id']

        read_only_fields = ['artist', 'views', 'likes']

        # content_type/object_id are set False because at POST (creation of
        # Artwork instance, there isn't yet a file content_type/object_id)
        # <for unexplainable reasons this 'required' option stopped working,
        # so I EXCLUDED the content_type and object_id fields. It works well
        # with CRUD>
        extra_kwargs = {
            'content_type': {'required': False},
            'object_id': {'required': False},
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

    # nested serialization
    follower = ArtistSerializer(many=False, read_only=True)
    following = ArtistSerializer(many=False, read_only=True)

    class Meta:
        model = Following
        fields = '__all__'
        extra_kwargs = {
            
        }
        

class ReactionSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    reaction_type = serializers.SerializerMethodField()

    def get_user(self,object):
        return object.user.username

    def get_reaction_type(self,object):
        return object.reaction_type.name

    class Meta:
        model = Reaction
        fields = ['reaction_type', 'user']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class CommentSerializer(serializers.ModelSerializer):

    user = UserReadOnlySerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }


class ReviewSerializer(serializers.ModelSerializer):

    user = UserReadOnlySerializer(many=False, read_only=True)

    category = serializers.SerializerMethodField() # ArtCategory

    '''An image media type belongs to the Image model
    All other file types belong to the File model'''
    caption_media_type = serializers.SerializerMethodField()
    body_media_type = serializers.SerializerMethodField()
    caption_media_url = serializers.SerializerMethodField()
    body_media_url = serializers.SerializerMethodField()
    # caption_media_model = serializers.SerializerMethodField()
    # body_media_model = serializers.SerializerMethodField()

    def get_category(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return object.category.name

    def get_caption_media_type(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        model_name = ContentType.objects.get_for_model(
        object.caption_media_object).model
        if model_name == 'image':
            return model_name
        elif model_name == 'file':
            return object.caption_media_object.file_type.name

    def get_body_media_type(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        if not object.body_media_object:
            return None

        model_name = ContentType.objects.get_for_model(
            object.body_media_object).model
        if model_name == 'image':
            return model_name
        elif model_name == 'file':
            return object.body_media_object.file_type.name

    def get_caption_media_url(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return object.caption_media_object.resource.url

    def get_body_media_url(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        if not object.body_media_object:
            return None

        return object.body_media_object.resource.url

    # def get_caption_media_model(self,object):
    #     model_name = ContentType.objects.get_for_model(
    #         object.caption_media_object).model
    #     return model_name

    # def get_body_media_model(self,object):
    #     model_name = ContentType.objects.get_for_model(
    #         object.body_media_object).model
    #     return model_name

    class Meta:
        model = Review
        fields = '__all__'

        # media_types and IDs are set False because at POST (creation of
        # Review instance, there isn't yet a file resource to provide the 
        # media type/media id)
        extra_kwargs = {
            'caption_media_type': {'required': False},
            'caption_media_id': {'required': False},
            'body_media_type': {'required': False},
            'body_media_id': {'required': False}
        }
        

class ArticleSerializer(serializers.ModelSerializer):

    user = UserReadOnlySerializer(many=False, read_only=True)

    # write_only so that an instance can be serialized without this field,
    # even though it has been set as {required: True} in kwargs
    html = serializers.CharField(write_only=True)

    html_url = serializers.SerializerMethodField()

    thumbnail_url = serializers.SerializerMethodField()

    def get_html_url(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return object.html_file.resource.url
    
    def get_thumbnail_url(self,object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return object.thumbnail_image.resource.url
    
    class Meta:
        model = Article
        fields = '__all__'

        # html_file 'required' is set False because at POST (creation of
        # Article instance, there isn't yet a file for it).
        # HOWEVER, for html it is set to True because it carries the html
        # content which is needed to create the html file.
        extra_kwargs = {
            'html_file': {'required': False},
            'html': {'required': True},
        }


class ProductCategorySerializer(serializers.ModelSerializer):

    root = serializers.SerializerMethodField()

    def get_root(self, object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return object.root.name


    class Meta:
        model = ProductCategory
        exclude = ['parent']


class SellerSerializer(serializers.ModelSerializer):

    user = UserReadOnlySerializer(many=False, read_only=True)

    class Meta:
        model = Seller
        fields = '__all__'


class ProductRatingSerializer(serializers.ModelSerializer):

    user = UserReadOnlySerializer(many=False, read_only=True)

    class Meta:
        model = ProductRating
        fields = '__all__'


class LicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = License
        fields = '__all__'


class ProductXLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductXLicense
        fields = '__all__'


class ProductItemSerializer(serializers.ModelSerializer):

    licenses = LicenseSerializer(many=True)
    file = serializers.SerializerMethodField()

    def get_file(self, object):
        try:
            object.pk # object has id.
        except:
            return None
        
        return{
            'name': object.file.filename,
            'size': object.file.filesize,
            'extension': object.file.extension
        }
        

    class Meta:
        model = ProductItem
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    thumbnail_images = serializers.SerializerMethodField()
    category = ProductCategorySerializer(many=False)
    seller = SellerSerializer(many=False)
    ratings = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    items = ProductItemSerializer(many=True)
    license_data = serializers.SerializerMethodField()

    # (model @property): the price of the CHEAPEST license for this product
    price = serializers.SerializerMethodField()

    def get_thumbnail_images(self, product):
        try:
            product.pk # object has id.
        except:
            return None
        
        image_urls = list(map(
            lambda i:i.resource.url, product.thumbnail_images.all()))
        return image_urls
    
    def get_ratings(self, product):
        try:
            product.pk # object has id.
        except:
            return None
        
        ratings = product.ratings
        return ProductRatingSerializer(ratings, many=True).data

    def get_stats(self, product):
        try:
            product.pk # object has id.
        except:
            return None
        
        ratings_count = product.ratings.count()
        ratings_sum = sum(list(map(lambda p:p.stars, product.ratings.all())))
        rating_average = round(ratings_sum/ratings_count,1) \
            if ratings_count else None
        reviews_count = product.comments.filter(parent_comment=None).count()
        
        return {
            'ratings_count': ratings_count,
            'rating_average': rating_average,
            'reviews_count': reviews_count

        }
    
    def get_license_data(self, product):
        try:
            product.pk # object has id.
        except:
            return None
        
        # get related Product X License through table instances
        productXlicenses = ProductXLicense.objects.filter(product__id=product.id)
        serialized_productXlicenses = ProductXLicenseSerializer(
            productXlicenses, many=True)
        
        return serialized_productXlicenses.data
    
    def get_price(self, product):
        try:
            product.pk # object has id.
        except:
            return None
        
        return product.price
    
    class Meta:
        model = Product
        fields = '__all__'


class ContestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contest
        fields = '__all__'
        