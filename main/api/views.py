from django.shortcuts import render, redirect
import json
import time
from django.conf import settings
import random
import os
from typing import Type, Any

# models
from main.models import (
    Artist, Artwork, File, FileType, FileGroup, ArtCategory, Image, Following,
    ReactionType, Reaction, ViewLog, Comment, SiteConfigurations, Review,
    Article, ArticleCategory, ProductCategory, Product, Seller, License,
    ProductXImage, ProductItem, ProductXLicense, ProductItemXLicense, Contest,
    ProductLibrary, ProductLibraryXXProductXLicense)
from user.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# serializers
from .serializers import (
    ArtworkSerializer, ArtistSerializer, ArtCategorySerializer,
    FollowingSerializer, ReactionSerializer, CommentSerializer,
    ReviewSerializer, ArticleSerializer, ProductSerializer, SellerSerializer,
    ProductItemSerializer, LicenseSerializer, ContestSerializer,
    UserReadOnlySerializer)

# response / status
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import FileResponse

# class-based API views
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins

# authentication
from django.contrib.auth import authenticate, login

# jwt authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.api.views import get_jwt_access_tokens_for_user

# permissions
from .permissions import (IsAuthenticated, IsAuthenticatedElseReadOnly,
IsArtworkAuthorElseReadOnly,IsArtistUserElseReadOnly,
IsCommentAuthorElseReadOnly,
IsReviewersGroupMemberAndReviewAuthorOrApprovedReadonly,
IsReviewersGroupMemberOrApprovedReadonly,
IsArticleCreatorsGroupMemberOrApprovedReadonly,
IsArticleCreatorsGroupMemberOrReadonly, IsProductSellerElseReadOnly,
IsContestCreatorsGroupMemberOrReadonly)

# File handling
import io
from django.core.files import File as DjangoFile
from django_drf_filepond.models import TemporaryUpload

# web/html parsing
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# pagination
from .pagination import (ArtworkPaginationConfig, ArtistPaginationConfig,
FollowPaginationConfig, ReactionPaginationConfig, CommentPaginationConfig,
ReviewPaginationConfig, ArticlePaginationConfig, ProductPaginationConfig,
SellerPaginationConfig, ContestPaginationConfig)

# caching
from django.core.cache import cache


def store_filepond_upload(upload_id,model_class:Type[Any],file_group:str,file_type=None) -> object:
            # MOVING (not copying) TEMPORARY FILE TO PERMANT FILE
            # first create fake permanent file from wrapped empty in-memory file (to get the permanent file path)
            # DELETE the fake permanent file
            # move temporary uploaded file to path of deleted fake permant file via os rename
            temp_upload = TemporaryUpload.objects.get(upload_id=upload_id)

            # create Image instance with empty resource to get path for moving temporary upload
            empty_file = io.StringIO('')
            empty_file.name = temp_upload.upload_name
            empty_resource = DjangoFile(empty_file)
            model_instance = model_class(file_group=FileGroup.objects.get(name='products'))
            if file_type:
                model_instance.file_type = file_type
            model_instance.resource = empty_resource
            model_instance.save()
            save_path = model_instance.resource.path

            # delete empty file from permanent save path and replace with temp file
            os.remove(save_path)
            os.rename(temp_upload.get_file_path(), save_path)
            # delete the temporary upload object
            temp_upload.delete()

            return model_instance


class ArtworkList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsAuthenticatedElseReadOnly]
    pagination_class = ArtworkPaginationConfig
    ordering = '-id'

    serializer_class = ArtworkSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        # get dictionary equivalent of POST data and add additional data
        data = request.POST.dict()  # {'title': title, 'content': content,...}
        data['artist'] = self.request.user.artist

        # print(f"ORDERED_DICT: {data}\n\n\n")
        '''
        print(data) give data in this form:

        {'title': 'testing artwork serializer', 'category': '6',
        'description': 'any descr', 'tags': 'any tags', 'file_type': 'image', 
        'artist': <Artist: Artist2 | aladdin>}
        '''

        serializer = ArtworkSerializer(data=data)

        if serializer.is_valid():
            try: 
                data['category'] = ArtCategory.objects.get(id=data['category'])            
                
                # the uploaded file must be wrapped into a file object
                wrapped_request_file = DjangoFile(request.FILES['file'])

                file_type = FileType.objects.get(name=data['file_type'])
                file_group = FileGroup.objects.get(name='artworks')
            except Exception as e:
                return Response({'error': 'make sure to select a file!'},
                 status=status.HTTP_400_BAD_REQUEST)

            # create (Image or File) FieldFile instance using the file object
            if file_type.name == 'image':
                
                file = Image(
                    file_group=file_group,resource=wrapped_request_file)
            else:
                file = File(
                    file_type=file_type, file_group=file_group,
                    resource=wrapped_request_file)

            file.save()

            # data["file"] = file
            data["content_type"] = ContentType.objects.get_for_model(file)
            data["object_id"] = file.id
            data["content_object"] = file

            # remove unrelated data from dictionary before creating Artist
            data.pop('file_type')

            artwork = Artwork(**data)
            artwork.save()

            output_data = serializer.data
            output_data["file_url"] = artwork.content_object.resource.url           

            return Response(output_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_queryset(self):
        '''general rule to retain logical coherence:
        - valid terms pass through a query filter() method
        - invalid terms return an empty queryset ( ModelName.objects.none() )'''

        # get the search term submitted with GET
        search_term = self.request.GET.get('search')
        filter = self.request.GET.get('filter')

        random_sample = self.request.GET.get('random_sample')
        random_sample_size = self.request.GET.get('random_sample_size')

        artworks_query = Artwork.objects

        # filter based on those liked (or reacted on) by user with username
        liked_by:str = self.request.GET.get('liked_by')
        if liked_by:
            some_user = User.objects.filter(username=liked_by).first()
            if some_user:
                artworks_query = artworks_query.filter(
                    reactions__user=some_user)
            else:
                return Artwork.objects.none()


        # filter based on search term/filter parameter
        if search_term:
            # filter example format: <model field>__icontains=<search term>
            if filter == 'title':
                artworks_query = artworks_query.filter(
                                title__icontains=search_term)
            elif filter == 'category':
                artworks_query = artworks_query.filter(
                                category__name__icontains=search_term)
            elif filter == 'artist':
                artworks_query = artworks_query.filter(
                        artist__user__username__iexact=search_term)
            elif filter == 'username':
                artworks_query = artworks_query.filter(
                        artist__user__username__istartswith=search_term)
            elif filter == 'name':
                artworks_query = artworks_query.filter(
                        Q(artist__user__first_name__in=search_term)
                        | Q(artist__user__last_name__in=search_term)
                        )
            elif filter == 'tags':
                artworks_query = artworks_query.filter(
                                tags__icontains=search_term)
        
        
        '''Return a random sample from the entire query result
        '''
        if random_sample == 'true':
            try:
                random_sample_size = int(random_sample_size)
            except:
                pass
            else:
                # choose a number of random samples and return                
                if random_sample_size > artworks_query.count():
                    random_sample_size = artworks_query.count()
                    
                random_art_ids = random.sample(
                    [artwork.id for artwork in artworks_query.all()],
                    random_sample_size)
                
                # return this without ordering, as it is to be random
                return artworks_query.filter(id__in=random_art_ids).all()

        return artworks_query.order_by(self.__class__.ordering).all()

     
class ArtworkDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsArtworkAuthorElseReadOnly]

    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer

    def get(self, request, *args, **kwargs):
        # update record of number of views on this artwork        
        if request.user.is_authenticated:
            artwork = Artwork.objects.filter(id=kwargs['pk']).first()
            
            # only log view if artwork doesn't belong to current viewer
            if artwork and artwork.artist.user.username != request.user.username:
                artwork_type = ContentType.objects.get_for_model(Artwork)

                view_log = ViewLog.objects.filter(content_type=artwork_type, object_id=kwargs['pk'], user__username=request.user.username).first()
                
                if not view_log:
                    # create new ViewLog instance
                    new_view_log = ViewLog(
                        content_type=artwork_type,
                        object_id=kwargs['pk'],
                        content_object=artwork,
                        user=request.user
                    )
                    new_view_log.save()

                    
                    


        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ArtistList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsAuthenticatedElseReadOnly]
    pagination_class = ArtistPaginationConfig
    ordering = '-id'

    serializer_class = ArtistSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Artist.objects.order_by(self.__class__.ordering).all()


class ArtistDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsArtistUserElseReadOnly]

    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

    def get(self, request, *args, **kwargs):        
        # get by 'username' in addition to the default 'pk'
        username = kwargs.get("username")
        if username:
            artist = Artist.objects.filter(user__username=username).first()
            serializer = ArtistSerializer(artist, data={})
            if serializer.is_valid() and artist:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ArtCategoryList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = []
    # pagination_class = 
    ordering = 'id'

    serializer_class = ArtCategorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return ArtCategory.objects.order_by(self.__class__.ordering).all()


class FollowingList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsAuthenticatedElseReadOnly]
    pagination_class = FollowPaginationConfig

    ordering = '-id'

    serializer_class = FollowingSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        user = self.request.user
        other_user = User.objects.get(username=kwargs.get('other_user'))

        if user and other_user:
            if Following.objects.filter(
                follower=user.artist, following=other_user.artist).first():
                return Response(
                    {"status": "already followed"},
                    status=status.HTTP_400_BAD_REQUEST)

            following_instance = Following.objects.create(
                follower=user.artist, following=other_user.artist)

            serializer = FollowingSerializer(following_instance)        

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_queryset(self):
        # get the search term submitted with GET
        username = self.request.GET.get('username')
        filter = self.request.GET.get('filter')

        artist = Artist.objects.filter(user__username=username).first()

        if username:
            if artist:
                if filter == 'followers':
                    filtered_query = Following.objects.filter(following=artist).all()
                elif filter == 'following':
                    filtered_query = Following.objects.filter(follower=artist).all()

                # any following instance involving this artist
                elif filter == 'any-follow':
                    filtered_query = Following.objects.filter(
                        Q(follower=artist)
                        |Q(following=artist)).all()
                else:
                    raise ValueError("Invalid filter option")

                return filtered_query.order_by(self.__class__.ordering)

            else:
                raise ValueError("No such artist found")
        else:
            # return this query if search field is empty (e.g on page load)
            return Following.objects.order_by(self.__class__.ordering).all()


class FollowingStatus(APIView):

    # permission_classes = [set following permission here]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        other_user = User.objects.get(username=kwargs.get('other_user'))

        if user and other_user:
            user_follows_other = bool(Following.objects.filter(
                follower=user.artist, following=other_user.artist).first())
            other_follows_user = bool(Following.objects.filter(
                follower=other_user.artist, following=user.artist).first())
            return Response({
                "user_follows_other": user_follows_other,
                "other_follows_user": other_follows_user
            }, status=status.HTTP_200_OK)
            
        return Response(
                    {"error": "invalid other_user"},
                    status=status.HTTP_400_BAD_REQUEST)
                


class Unfollow(APIView):

    # permission_classes = [set following permission here]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        other_user = User.objects.get(username=kwargs.get('other_user'))

        if user and other_user:
            following_instance = Following.objects.filter(
                follower=user.artist, following=other_user.artist).first()
            if following_instance:
                following_instance.delete()
                return Response(
                    {"status": "unfollowed"},
                    status=status.HTTP_200_OK)

            else:
                return Response(
                    {"status": "not following"},
                    status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
                    {"error": "invalid other_user"},
                    status=status.HTTP_400_BAD_REQUEST)
                    

class ReactList(mixins.ListModelMixin, generics.GenericAPIView):
    #lists reactions on an instance of a model (artwork, post, etc)

    # no permissions required for this view
    permission_classes = []

    serializer_class = ReactionSerializer
    pagination_class = ReactionPaginationConfig
    ordering = '-id'

    def get(self, request, model:str, instance_id:int, *args, **kwargs):        
        response = self.list(request, *args, **kwargs)
        response.data['model'] = model
        response.data['instance_id'] = instance_id
        response.data['user_reactions'] = []

        content_type = ContentType.objects.get(model=model.lower())

        user_reaction_names = []
        if self.request.user.is_authenticated:
            reactions_by_user = Reaction.objects.filter(content_type=content_type, 
                            object_id=instance_id, user=request.user).order_by(
                                self.__class__.ordering).all()
            user_reactions_serialized = ReactionSerializer(reactions_by_user, many=True)

            user_reaction_names = [
                reaction['reaction_type'] for reaction in user_reactions_serialized.data]
            # response.data['user_reactions'] = user_reaction_names

        
        # format the response data in a cute, intuitive order
        cute_data = {
            "count": response.data["count"],
            "next": response.data["next"],
            "previous": response.data["previous"],
            "user_reactions": user_reaction_names,
            "results": response.data["results"]
        }
        response.data = cute_data

        # (OUTDATED!!) order the display of results in the json output (not too necessary)        
        # response.data.move_to_end('user_reactions', last=False)
        # response.data.move_to_end('instance_id', last=False)
        # response.data.move_to_end('model', last=False)
        # response.data.move_to_end('previous', last=False)
        # response.data.move_to_end('next', last=False)
        # response.data.move_to_end('count', last=False)

        return response


    def get_queryset(self):

        model = self.kwargs['model']
        instance_id = self.kwargs['instance_id']

        content_type = ContentType.objects.get(model=model.lower())
        # object_reacted_on = content_type.get_object_for_this_type(id=instance_id)

        reactions = Reaction.objects.filter(content_type=content_type, 
                        object_id=instance_id)
        # if self.request.user.is_authenticated:
        #     reactions = reactions.exclude(user=self.request.user)
        reactions = reactions.order_by(self.__class__.ordering).all()

        return reactions


class React(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, reaction_type_name:str, model:str, instance_id:int):

        content_type = ContentType.objects.get(model=model.lower())
        object_reacted_on = content_type.get_object_for_this_type(id=instance_id)

        user = self.request.user
        reaction_type = ReactionType.objects.get(name=reaction_type_name)
        is_duplicate_reaction = Reaction.objects.filter(
            content_type=content_type, object_id=instance_id, 
            user=user, reaction_type=reaction_type).first()
        if is_duplicate_reaction:
            return Response(
                {reaction_type_name: f"already reacted by current user on this {model}"},
                             status=status.HTTP_417_EXPECTATION_FAILED)

        # Create a new Reaction object for a specific object (artwork, post etc)
        reaction = Reaction(
        content_type=content_type,
        object_id=object_reacted_on.id,
        content_object=object_reacted_on,
        user=user,
        reaction_type=reaction_type
        )
        reaction.save()


        response_data = {
            "reaction": reaction_type_name,
            "model": model,
            "instance_id": instance_id,
            "user": self.request.user.username
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UnReact(APIView):

    # permission_classes: permission is tied to the logic for this view. Only 
    # user who reacted on an object can remove the reaction.

    def post(self, request, reaction_type_name:str, model:str, instance_id:int):

        content_type = ContentType.objects.get(model=model.lower())        
        object_reacted_on = content_type.get_object_for_this_type(id=instance_id)

        reaction_type = ReactionType.objects.get(name=reaction_type_name)

        try:
            reaction = Reaction.objects.get(content_type=content_type,
                                            object_id=object_reacted_on.pk,
                                            user=self.request.user,
                                            reaction_type=reaction_type)

        except Reaction.DoesNotExist:
            return Response(
                {"error": f"no '{reaction_type_name}' reaction from current user on this {model}"},
                                status=status.HTTP_404_NOT_FOUND)

        else:
            reaction.delete()        

        response_data = {
            "removed reaction": reaction_type_name
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CommentList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                    generics.GenericAPIView):
    permission_classes = [IsAuthenticatedElseReadOnly]
    pagination_class = CommentPaginationConfig

    serializer_class = CommentSerializer
    ordering = '-id'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        class CommentNotForPost(Exception):
            pass

        try:
            post_id = self.kwargs['pk']
            post_type = ContentType.objects.get(model=self.kwargs['model'])
            post = post_type.model_class().objects.get(id=post_id)

            parent_comment_id = self.request.GET.get('parent_comment')
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                if parent_comment.post_object.pk != post.pk:
                    raise CommentNotForPost
            else:
                parent_comment = None
            content = self.request.GET.get('content')
        except Comment.DoesNotExist:
            return Response({"error": "invalid parent_comment id"}, 
                                            status=status.HTTP_404_NOT_FOUND)
        except CommentNotForPost:
            return Response(
                {"error": f"post (id={post_id}) and parent_comment (post_id={parent_comment.post_object.pk}) do not match!"},
                                            status=status.HTTP_400_BAD_REQUEST)
        
        user = self.request.user
        
        new_comment = Comment.objects.create(
            user=user,
            post_type=post_type,
            post_id=post_id,
            post_object=post,            
            content=content,
            parent_comment=parent_comment
        )            

        serializer = CommentSerializer(new_comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        post_id = self.kwargs['pk']
        post_type = ContentType.objects.get(model=self.kwargs['model'])
        post = post_type.model_class().objects.get(id=post_id)
        comments = post.comments.order_by(self.__class__.ordering).all()
        return comments

        
class CommentDetail(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
 mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsCommentAuthorElseReadOnly]

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class SiteConfigurationsApi(APIView):

    permission_classes = []

    '''This is for use with the wagtail SiteConfigurations model, ultimately
    to have an API for retrieving wagtail custom settings'''
    def get(self, request, *args, **kwargs):
        # the object containing all the configuration settings for this site
        settings = SiteConfigurations.objects.first()

        data = {}

        if settings.default_profile_image:
            data['default_profile_image_url'] = settings.default_profile_image.file.url

        return Response(data, status=status.HTTP_200_OK)


class ReviewList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsReviewersGroupMemberOrApprovedReadonly]
    pagination_class = ReviewPaginationConfig
    ordering = '-id'

    serializer_class = ReviewSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Review.objects.order_by(self.__class__.ordering).filter(approved=True).all()

    def post(self, request, *args, **kwargs):        
        # get dictionary equivalent of POST data and add additional data
        data = request.POST.dict()  # {'title': title, 'content': content,...}
        data['user'] = self.request.user

        # print(f"ORDERED_DICT: {data}\n\n\n")

        # first serializer. Only the none-file fields are enforced in the
        # serializer class, so that the file is created only after the 
        # validation of the none-file data
        review_data_serializer = ReviewSerializer(data=data)

        if review_data_serializer.is_valid():
            # print("VALID SERIALIZER")
            # print("request.FILES:")
            # print(request.FILES)
            # print("DATA:")
            # print(data)

            # ---FILE PROCESSING---

            # caption file processing
            try: 
                data['category'] = ArtCategory.objects.get(id=data['category'])            
                
                # the uploaded file must be wrapped into a file object
                wrapped_request_file = DjangoFile(request.FILES['caption_file'])

                # read and immediately discard of the 'caption_file_type' entry
                # as it shouldn't be present when the data list is used to
                # create a Review object via Review(**data)
                caption_file_type = FileType.objects.get(name=data.pop('caption_file_type'))
                file_group = FileGroup.objects.get(name='reviews')
            except Exception as e:
                print(e.args)
                return Response({'error': 'Failed to process caption file!'},
                 status=status.HTTP_400_BAD_REQUEST)

            # create (Image or File) FieldFile instance using the file object
            if caption_file_type.name == 'image':
                
                caption_file = Image(
                    file_group=file_group,resource=wrapped_request_file)
            else:
                caption_file = File(
                    file_type=body_file_type, file_group=file_group,
                    resource=wrapped_request_file)

            caption_file.save()

            # data["file"] = file
            data["caption_media_type"] = ContentType.objects.get_for_model(caption_file)
            data["caption_media_id"] = caption_file.id
            data["caption_media_object"] = caption_file


            # body file processing (some redundant lines ommitted)
            if request.FILES.get('body_file'):
                try:            
                    # the uploaded file must be wrapped into a file object
                    wrapped_request_file = DjangoFile(request.FILES['body_file'])

                    # read and immediately discard of the 'body_file_type' entry
                    # as it shouldn't be present when the data list is used to
                    # create a Review object via Review(**data)
                    body_file_type = FileType.objects.get(name=data.pop('body_file_type'))
                except Exception as e:
                    print(e.args)
                    return Response({'error': 'Failed to process body file!'},
                    status=status.HTTP_400_BAD_REQUEST)

                # create (Image or File) FieldFile instance using the file object
                if body_file_type.name == 'image':
                    
                    body_file = Image(
                        file_group=file_group,resource=wrapped_request_file)
                else:
                    body_file = File(
                        file_type=body_file_type, file_group=file_group,
                        resource=wrapped_request_file)

                body_file.save()

                # data["file"] = file
                data["body_media_type"] = ContentType.objects.get_for_model(body_file)
                data["body_media_id"] = body_file.id
                data["body_media_object"] = body_file

            # creating Artist from data list, as all 'non-model' entries have
            # been popped out and used
            review = Review(**data)
            review.save()

            # now the review has been created, extra info such as the instance
            # id and the IDs/url paths of its files are present. So we create
            # a second serializer to capture all these info.
            review_instance_serializer = ReviewSerializer(review)           

            return Response(review_instance_serializer.data, status=status.HTTP_201_CREATED)
        return Response(review_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsReviewersGroupMemberAndReviewAuthorOrApprovedReadonly]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PendingReviews(APIView):
    '''just return number of unapproved reviews'''
    permission_classes = []

    def get(self, request):
        pending_reviews_count = Review.objects.filter(approved=False).count()
        
        return Response({
            'pending_reviews': pending_reviews_count},
            status=status.HTTP_200_OK)
    

class ArticleList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    # TODO: CHANGE THIS permission back to the one with 'ApprovedReadonly
    permission_classes = [IsArticleCreatorsGroupMemberOrReadonly] # [IsArticleCreatorsGroupMemberOrApprovedReadonly]
    pagination_class = ArticlePaginationConfig
    ordering = '-id'

    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Article.objects.order_by(self.__class__.ordering).all()

    def post(self, request, *args, **kwargs):       
        # get dictionary equivalent of POST data and add additional data
        data = request.POST.dict()  # {'title': title, 'content': content,...}
        data['user'] = self.request.user

        # print(f"ORDERED_DICT: {data}\n\n\n")

        serializer = ArticleSerializer(data=data)

        if serializer.is_valid():
            # print("VALID SERIALIZER")
            # print("request.FILES:")
            # print(request.FILES)
            # print("DATA:")
            # print(data)


            # ---FILE PROCESSING---           
            html = data.pop('html')

            # process the html images
            html_soup = BeautifulSoup(html, 'html.parser')            
            src_id_mapping = {}

            # goals:
            # - for each blob img element,
                # - create image file
                # - update its src with the file URL
                # - store src_id mapping in database
                # - set it as thumbnail_image if it's the first blob img
            # NOTE: keep the URLs (in html file and src_id mapping) RELATIVE, 
            # for ease of management in case project media_url changes
            for img in html_soup.find_all('img'):
                src = img.get('src')

                # skip non-blob img elements
                if not src.startswith('blob:'):
                    continue             

                try:           
                    # wrap request file into a file object
                    request_file = request.FILES[src]
                    wrapped_request_file = DjangoFile(request_file)

                    file_group = FileGroup.objects.get(name='articles')
                except Exception as e:
                    print(e.args)
                    return Response({'error': 'Failed to process article image!'},
                    status=status.HTTP_400_BAD_REQUEST)

                # create Image instance
                article_image_file = Image(
                        file_group=file_group,resource=wrapped_request_file)

                article_image_file.save()

                # update src and get src_id mapping
                img['src'] = article_image_file.resource.url
                src_id_mapping[img['src']] = article_image_file.id

                # set it as thumbnail_image if it's the first blob img
                if not data.get('thumbnail_image'):
                    data['thumbnail_image'] = article_image_file
            
            # update html with processed src urls
            html = str(html_soup)


            # process the html file
            # html content will be used to create an in-memory file, which
            # is then wrapped into a file object
            try:
                in_memory_file = io.StringIO(html)
                in_memory_file.name = \
                    f"article{time.time()}.html" # file must have a name
                wrapped_in_memory_file = DjangoFile(in_memory_file)                

                file_type = FileType.objects.get(name='web')
                file_group = FileGroup.objects.get(name='articles')
            except Exception as e:
                print(e.args)
                return Response({'error': 'Error in upload. Check the fields.'},
                 status=status.HTTP_400_BAD_REQUEST)

            # create FieldFile instance using the file object            
            html_file = File(
                    file_type=file_type, file_group=file_group,
                    resource=wrapped_in_memory_file)
            html_file.save()            

            #----------------------------------------

            data["html_file"] = html_file
            data["html_images"] = src_id_mapping

            article = Article(**data)
            article.save()

            article_instance_serializer = ArticleSerializer(article)                      

            return Response(article_instance_serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ArticleDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = []

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # DIAGNOSIS ONLY
        # print(f"\nrequest: {request}")
        # print(f"\nargs: {args}")
        # print(f"\nkwargs: {kwargs}")
        # return Response({'test': 'ok'})

        # get the request items in the form of a normal dictionaey
        data = request.POST.dict()

        article = Article.objects.get(id=kwargs['pk'])
        html = data['html']

        # process the html images
        html_soup = BeautifulSoup(html, 'html.parser')            
        src_id_mapping = article.html_images

        # goals:
        # - for each src in src_id mapping,
            # if there is no img element in
                    # new html having matching src, delete the image instance
                    # and remove it from the src_id mapping
            # NOTE: keep the URLs (in html file and src_id mapping) RELATIVE, 
            # for ease of management in case project media_url changes
        # - for each blob img element,
            # - create image file
            # - update its src with the file URL
            # - store src_id mapping in database
        # - get first img in html SOUP, get the Image instance having matching
            # src, and set it as thumbnail_image


        # delete any existing image instance no longer referenced in the HTML
        for src, id in src_id_mapping.items():
            if not html_soup.find(name='img', src=src):
                Image.objects.get(id=id).delete()
                del src_id_mapping[src]            


        for img in html_soup.find_all('img'):
            src = img.get('src')

            # skip non-blob img elements
            if not src.startswith('blob:'):
                continue             

            try:           
                # wrap request file into a file object
                request_file = request.FILES[src]
                wrapped_request_file = DjangoFile(request_file)

                file_group = FileGroup.objects.get(name='articles')
            except Exception as e:
                print(e.args)
                return Response({'error': 'Failed to process article image!'},
                status=status.HTTP_400_BAD_REQUEST)

            # create Image instance
            article_image_file = Image(
                    file_group=file_group,resource=wrapped_request_file)

            article_image_file.save()

            # update src and get src_id mapping
            img['src'] = article_image_file.resource.url
            src_id_mapping[img['src']] = article_image_file.id
            article.html_images = src_id_mapping

            # set first img as thumbnail_image (using updated src_id mapping)
            first_soup_img = html_soup.find('img')
            first_soup_img_id = src_id_mapping[first_soup_img.get('src')]
            first_soup_img_instance = Image.objects.get(id=first_soup_img_id)
            article.thumbnail_image = first_soup_img_instance

            article.save()

        # -----------------------------------------------------

        # write the updated html content to the html file
        file_stream = article.html_file.resource
        file_stream.open('w')
        file_stream.write(str(html_soup))
        file_stream.close()

        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

class ProductCategoryList(APIView):

    permission_classes = []

    def get(self, request, *args, **kwargs):
        trees = cache.get('product_category_trees')
        if not trees:
            trees = ProductCategory.trees(jsonify=True)
        data = {
            'product_categories': trees
        }
        
        return Response(data, status=status.HTTP_200_OK)


class ProductList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsProductSellerElseReadOnly]
    pagination_class = ProductPaginationConfig
    ordering = '-id'

    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)    

    def get_queryset(self):
        seller = self.request.GET.get('seller') # the seller alias
        products_query = Product.objects

        # id of product to exclude (e.g current product on a detail page)
        exclude_id = self.request.GET.get('exclude_id')

        # only include products if they are listed or belong to user
        # (even if unlisted), but skip this filter if user is superuser
        if not self.request.user.is_superuser:
            products_query = products_query.filter(
                Q(listed=True) | Q(seller__user__id=self.request.user.id)
                )

        # filter by seller alias
        if seller:
            try:
                seller = Seller.objects.get(alias=seller)
                products_query = products_query.filter(seller=seller)
            except:
                return Product.objects.none()
            
        # exclude certain product(s)
        products_query = products_query.exclude(id=exclude_id)

        # filter by category tree
        subcategory_path = self.kwargs.get('subcategory_path')
        if subcategory_path:
            '''get all products with one of the following conditions:
            - its category path starts with the queried subcategory path in
            terms of url pattern, not just spelling 
                (e.g /tutorials/books-comics/ starts with /tutorials/
                    but not with /tutor/)
                OR
            - its category path matches the queried subcategory path
                (e.g /tutorials matches with /tutorials)
            '''
            return products_query.filter(
                # use an ending '/' to ensure that the 'startswith' condition
                # doesn't get confused with a 'similar-spelling' problem.
                # Such as where the queried subcategory path is '/tutor' and
                # it wrongly gets taken as a starting path to
                # /tutorials/books-comics/, thereby including
                # products with the path: /tutorials/books-comics/
                Q(category__path__istartswith=f"/{subcategory_path}/")
                 |
                Q(category__path=f"/{subcategory_path}")).order_by(
                    self.__class__.ordering).all()
        return products_query.order_by(self.__class__.ordering).all()
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # title = data['title']
        # category = data['category']
        # description = data['description']
        # product_file_datas = data['product_files']
        # sample_image_datas = data['sample_images']
        # product_licenses = data['product_licenses']

        '''models instances to be created
        ---primary models---
        - Product (from product data)
        - ProductItem <-- File (from product_files)
        ---secondary models (custom through tables for manytomanyrelationships---
        - ProductXImage <-- Image (from sample_images)
        - ProductXLicense (from product_licenses)
        - ProductItemXLicense (from product_file_datas)
        '''

        # CREATE PRODUCT INSTANCE
        # get just the data for creating a Product instance from dictionary
        product_fields = [field.name for field in Product._meta.get_fields()]
        product_data = {key:value for key, value in data.items() if key in product_fields} # TODO: add serializer validation here
        product_data['category'] = ProductCategory.objects.get(id=product_data['category'])
        product_data['seller'] = request.user.seller
        product = Product(**product_data)
        product.save()

        # CREATE PRODUCT IMAGES
        sample_image_ids = [file_data['file']['serverId'] for file_data in data['sample_images']]
        for id in sample_image_ids:
            sample_image = store_filepond_upload(
                upload_id=id, model_class=Image, file_group='products')
            product_image = ProductXImage(product=product, image=sample_image)
            product_image.save()
        

        # CREATE PRODUCT LICENSES
        for license in data['product_licenses']:
            product_license = ProductXLicense(
                product=product,
                license = License.objects.get(id=license['id']),
                price = license['price'] if license.get('price') else 0
            )
            product_license.save()

        # CREATE PRODUCT ITEMS (files) AND PRODUCT LICENSES
        for product_file_data in data['product_files']:
            try:
                # if no errors but blank file type
                file_type_name=product_file_data['file']['fileType'].split('/')[0]
                if file_type_name.strip() == "":
                    file_type_name = 'other'
            except:
                # if any errors
                file_type_name = 'other'
            finally:
                file_type, newly_created = FileType.objects.get_or_create(
                    name=file_type_name)
            
            product_file = store_filepond_upload(
                upload_id=product_file_data['file']['serverId'], model_class=File,
                file_group='products', file_type=file_type)
            product_item = ProductItem(product=product, file=product_file)
            product_item.save()

            file_licenses = product_file_data['licenses']
            for license in file_licenses:
                product_item_license = ProductItemXLicense(
                    product_item=product_item, license=License.objects.get(id=license['id']))
                product_item_license.save()

        print("ran all product calls successfully")         

        return Response(status=status.HTTP_200_OK)


class ProductDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsProductSellerElseReadOnly]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    

class UnlistProduct(APIView):

    permission_classes = [IsProductSellerElseReadOnly]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        product_id = data['product_id']
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        product.listed = False
        product.save()
        return Response({'executed command':'unlist',
                         'product id': product_id}, status=status.HTTP_200_OK)


class ListProduct(APIView):
    '''mark the product as listed to be publicly viewable in the product gallery'''

    permission_classes = [IsProductSellerElseReadOnly]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        product_id = data['product_id']
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        product.listed = True
        product.save()
        return Response({'executed command':'list',
                         'product id': product_id}, status=status.HTTP_200_OK)
    

class SellerList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):
    permission_classes = [IsAuthenticatedElseReadOnly]
    pagination_class = SellerPaginationConfig
    ordering = '-id'

    serializer_class = SellerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Seller.objects.order_by(self.__class__.ordering).all()
    
    def post(self, request, *args, **kwargs):

        # get dictionary equivalent of POST data and add additional data
        data = request.POST.dict()
        data['user'] = request.user

        # first ensure that current user has no seller instance
        existing_seller_profile = Seller.objects.filter(user=request.user).first()
        if existing_seller_profile:
            return Response({'error': 'user has existing seller profile'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # also ensure that this alias is not already owned elsewhere
        duplicate_seller_credentials = Seller.objects.filter(
            Q(alias=data.get('alias'))|Q(brand_name=data.get('brand_name'))
        ).first()
        if duplicate_seller_credentials:
            return Response({'error': 'a seller profile already exists with these credentials'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            seller = Seller(**data)
        except:
            return Response({'error': 'incorrect/incomplete seller fields given'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            seller.save()
            return Response(SellerSerializer(seller).data,
                status=status.HTTP_201_CREATED)    
    

class SellerDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsProductSellerElseReadOnly]

    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    def get(self, request, *args, **kwargs):        
        # get seller by 'alias' in addition to the default 'pk'
        alias = kwargs.get("alias")
        if alias:
            seller = Seller.objects.filter(alias=alias).first()
            serializer = SellerSerializer(seller, data={})
            if serializer.is_valid() and seller:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        
        # get seller instance of current user if no alias and no pk (from url)
        elif request.user.is_authenticated and not kwargs.get("pk"):
            seller = Seller.objects.filter(user=request.user).first()
            if seller:
                return Response(SellerSerializer(seller).data,
                                status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        
        elif (not request.user.is_authenticated) and (not kwargs.get("pk")):
            return Response({'error': 'must be logged in to use this endpoint'},
                            status=status.HTTP_401_UNAUTHORIZED)


        # return seller instance based on pk supplied in url params
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    

class LicenseList(APIView):
    permission_classes = []

    def get(self, request):
        # TEMPORARY: only make free license available for now
        licenses = License.objects.filter(free=True).all()

        
        serialized_licenses = LicenseSerializer(licenses, many=True).data
        
        return Response(serialized_licenses, status=status.HTTP_200_OK)
    

class ContestList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsContestCreatorsGroupMemberOrReadonly]
    pagination_class = ContestPaginationConfig
    ordering = '-id'

    serializer_class = ContestSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Contest.objects.order_by(self.__class__.ordering).all()
    

class ContestDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsContestCreatorsGroupMemberOrReadonly]

    queryset = Contest.objects.all()
    serializer_class = ContestSerializer

    def get(self, request, *args, **kwargs):    
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

class RandomContest(APIView):
    '''simply get a random contest for display in contest page ad banner'''

    permission_classes = []

    def get(self, request, *args, **kwargs):

        # get contests with id different from exclude_id

        other_contests = Contest.objects.exclude(id=kwargs['exclude_id'])
        if other_contests.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # limit to the last 100 for speed of execution in further operations
        other_contests_list = list(other_contests)[-100:] 
        random.shuffle(other_contests_list) # shuffle in-place
        random_contest = random.choice(other_contests_list)

        data = ContestSerializer(random_contest).data
        return Response(data, status=status.HTTP_200_OK)


class ProductLibraryAdd(APIView):
    '''adds a license for a product to the user's product library'''

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        try:
            product = Product.objects.get(id=data['product_id'])
            license = License.objects.get(id=data['license_id'])
            productxlicense = ProductXLicense.objects.get(product=product, license=license)
        except:
            return Response({'error':'no product with this license'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_product_library, created = \
            ProductLibrary.objects.get_or_create(user=request.user)
        
        product_libraryXXproductxlicense, created = \
            ProductLibraryXXProductXLicense.objects.get_or_create(
                product_library=user_product_library, 
                productxlicense=productxlicense)
        if created:
            return Response({'message':'added to library'},status=status.HTTP_201_CREATED)
        return Response({'message': 'already added'}, status=status.HTTP_200_OK)
    

class ProductLibraryList(APIView):
    '''list all the product licenses in this user's product library, or for a 
    specific product if the product_id is specified as a query parameter'''

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')

        user_product_library = ProductLibrary.objects.filter(
            user=request.user).first()
        
        if not user_product_library:
            # data returned should depend on if fetching for a specific product
            # or not, to decide whether to use a list or not
            empty_data = None if product_id else []
            return Response(empty_data,
                            status=status.HTTP_200_OK)
        
        else:

            # if fetching for a specific product
            if product_id:
                productxlicenses = user_product_library.productxlicenses.filter(
                    product_id=product_id
                )
                productxlicenses_to_licenses = lambda x:x.license                
                licenses = list(map(productxlicenses_to_licenses,productxlicenses))
                return Response(LicenseSerializer(licenses,many=True).data,
                                status=status.HTTP_200_OK)
            
            # fetching for all products which user has added to library
            else:
                productxlicenses = user_product_library.productxlicenses.all()
                productxlicenses_to_products_and_licenses = lambda x:{
                    'product': ProductSerializer(x.product, many=False).data,
                    'owned_license': LicenseSerializer(x.license, many=False).data
                }
                products_and_licenses = list(map(
                    productxlicenses_to_products_and_licenses,productxlicenses))
                return Response(products_and_licenses,
                                status=status.HTTP_200_OK)


class ProductDownload(APIView):
    '''TODO: the error responses in this view should be API responses, NOT
    rendered templates. The solution currently employed is just used as a
    quick fix at the moment, and should be handled by the frontend instead.'''

    # permissions are removed so anonymous users can download free resources
    permission_classes = []

    def get(self, request, *args, **kwargs):
        
        product_id = kwargs.get('product_id')
        license_id = kwargs.get('license_id')
        file_id = kwargs.get('file_id')

        # first get the product_item having this product, license and file
        try:
            product_item = ProductItem.objects.get(
                product__id=product_id,
                licenses__id=license_id,
                file__id=file_id)
        except:
            error_msg = 'no such product with the given license and file'
            return render(request, 'main/download_restricted.html',
                          {'error_msg':error_msg})
        
        # now that the product, license and file are confirmed, do a quick
        # check if the license is free, so as to skip further authentication
        # checks if required and thus make it possible for anonymous users
        # (not signed in) to download free resources without needing to login
        license = License.objects.get(id=license_id)
        if not license.name.lower() == 'free':
            if not request.user.is_authenticated:
                error_msg = 'you must be logged in to download this resource!'
                return render(request, 'main/download_restricted.html',
                          {'error_msg':error_msg})

            try:
                # if this returns None, it means user has no rights to this
                # license for this particular product, and thus no rights to 
                # any file under this license for this particular product.
                # Even if user might have a product library already.
                productxlicense = request.user.product_library.productxlicenses.filter(
                    product__id=product_id, license__id=license_id).first()
            except:
                # user has no product library hence no rights to 
                # any file under this license for this product
                productxlicense = None
            
            if not productxlicense:
                error_msg = 'user has no ownership of this license for this product'
                return render(request, 'main/download_restricted.html',
                          {'error_msg':error_msg})
        
        file = File.objects.get(id=file_id)
        file_path = file.resource.path        

        return FileResponse(
            open(file_path, 'rb'), as_attachment=True, filename=file.filename)


class ArtistProfileSave(APIView):
    '''updates the artist and user instances based on changes made in the
    ArtistPortfolio page at the frontend'''

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        try:
            first_name = data['firstName'].strip()
            last_name = data['lastName'].strip()
            location = data['location']
            bio = data['bio']
            website = data['website']
            tools = data['tools']
            profile_image = request.FILES.get('profileImage')

            wrapped_profile_image = DjangoFile(profile_image)

            assert first_name != ''
            assert last_name != ''
        except:
            return Response(
                {'error':'error saving profile. ensure to submit required fields'},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            # save artist fields
            artist = Artist.objects.get(user=request.user)
            artist.location = location
            artist.bio = bio
            artist.website = website
            artist.tools = tools
            artist.save()

            # save user fields
            artist.user.first_name = first_name
            artist.user.last_name = last_name
            if profile_image:
                artist.user.profile_image = wrapped_profile_image
            artist.user.save()

            return Response({
                'msg': 'profile save successful',
                'artist': ArtistSerializer(artist).data,
                'user': UserReadOnlySerializer(artist.user).data},
                                    status=status.HTTP_200_OK)
    