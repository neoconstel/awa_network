from django.shortcuts import render, redirect
import json
from django.conf import settings

# models
from main.models import (
    Artist, Artwork, File, FileType, FileGroup, ArtCategory, Image, Following,
    ReactionType, Reaction)
from user.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# serializers
from .serializers import (
    ArtworkSerializer, ArtistSerializer, ArtCategorySerializer,
    FollowingSerializer, ReactionSerializer)

# response / status
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# class-based API views
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins

# authentication
from django.contrib.auth import authenticate, login

# permissions
from .permissions import (IsAuthenticated, IsAuthenticatedElseReadOnly,
IsArtworkAuthorElseReadOnly,IsArtistUserElseReadOnly)

# jwt authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.api.views import get_jwt_access_tokens_for_user

# File handling
from django.core.files import File as DjangoFile

# pagination
from .pagination import (ArtworkPaginationConfig, ArtistPaginationConfig,
FollowPaginationConfig)


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
        # get the search term submitted with GET
        search_term = self.request.GET.get('search')
        filter = self.request.GET.get('filter')

        if search_term:
            # filter example format: <model field>__icontains=<search term>
            if filter == 'title':
                filtered_query = Artwork.objects.filter(
                                title__icontains=search_term).all()
            elif filter == 'category':
                filtered_query = Artwork.objects.filter(
                                category__name__icontains=search_term).all()
            elif filter == 'artist':
                filtered_query = Artwork.objects.filter(
                        artist__user__username__iexact=search_term).all()
            elif filter == 'username':
                filtered_query = Artwork.objects.filter(
                        artist__user__username__istartswith=search_term).all()
            elif filter == 'name':
                filtered_query = Artwork.objects.filter(
                        Q(artist__user__first_name__in=search_term)
                        | Q(artist__user__last_name__in=search_term)
                        ).all()
            elif filter == 'tags':
                filtered_query = Artwork.objects.filter(
                                tags__icontains=search_term).all()
            return filtered_query.order_by(ArtworkList.ordering)
        else:
            # return this query if search field is empty (e.g on page load)
            return Artwork.objects.order_by(ArtworkList.ordering).all()

     
class ArtworkDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, generics.GenericAPIView):

    permission_classes = [IsArtworkAuthorElseReadOnly]

    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer

    def get(self, request, *args, **kwargs):
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
        return Artist.objects.order_by(ArtistList.ordering).all()


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
        return ArtCategory.objects.order_by(ArtCategoryList.ordering).all()


class FollowingList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    # permission_classes = [set following permission here]
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

                return filtered_query.order_by(FollowingList.ordering)

            else:
                raise ValueError("No such artist found")
        else:
            # return this query if search field is empty (e.g on page load)
            return Following.objects.order_by(FollowingList.ordering).all()


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
                    

class ReactList(APIView):

    # no permissions required for this view
    permission_classes = []

    def get(self, request, model:str, instance_id:int):

        content_type = ContentType.objects.get(model=model.lower())
        # object_reacted_on = content_type.get_object_for_this_type(id=instance_id)

        reactions = Reaction.objects.filter(content_type=content_type, 
                        object_id=instance_id).all()

        serializer = ReactionSerializer(reactions, many=True)

        response_data = {
            "model": model,
            "instance_id": instance_id,
            "reactions": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class React(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, reaction_type:str, model:str, instance_id:int):

        content_type = ContentType.objects.get(model=model.lower())
        object_reacted_on = content_type.get_object_for_this_type(id=instance_id)

        user = self.request.user
        reaction_type_instance = ReactionType.objects.get(name=reaction_type)
        is_duplicate_reaction = Reaction.objects.filter(
            content_type=content_type, object_id=instance_id, 
            user=user, reaction_type=reaction_type_instance).first()
        if is_duplicate_reaction:
            return Response(
                {reaction_type: f"already reacted by current user on this {model}"},
                             status=status.HTTP_417_EXPECTATION_FAILED)

        # Create a new Reaction object for a specific object (artwork, post etc)
        reaction = Reaction(
        content_type=content_type,
        object_id=object_reacted_on.id,
        content_object=object_reacted_on,
        user=user,
        reaction_type=reaction_type_instance
        )
        reaction.save()


        response_data = {
            "reaction": reaction_type,
            "model": model,
            "instance_id": instance_id,
            "user": self.request.user.username
        }
        return Response(response_data, status=status.HTTP_200_OK)



        # return Response({'test':'OK', 'instance_id': instance_id}, status=status.HTTP_200_OK)