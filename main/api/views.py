from django.shortcuts import render, redirect
import json
from django.conf import settings

# models
from main.models import (
    Artist, Artwork, File, FileType, FileGroup, ArtCategory)
from user.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# serializers
from .serializers import ArtworkSerializer, ArtistSerializer

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
from .permissions import (IsAuthenticatedElseReadOnly,
IsArtworkAuthorElseReadOnly,IsArtistUserElseReadOnly)

# jwt authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.api.views import get_jwt_access_tokens_for_user

# Static/Media
from django.core.files.storage import FileSystemStorage

# pagination
from .pagination import ArtworkPaginationConfig, ArtistPaginationConfig


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
            # create a post instance using the POST data
            data['category'] = ArtCategory.objects.get(id=data['category'])

            from django.core.files import File as DjangoFile
            
            # the uploaded file must be wrapped into a file object
            wrapped_request_file = DjangoFile(request.FILES['file'])

            file_type = FileType.objects.get(name=data['file_type'])
            file_group = FileGroup.objects.get(name='artworks')

            # create a FieldFile instance using the file object
            file = File(
                file_type=file_type, file_group=file_group,
                 resource=wrapped_request_file)

            file.save()
            data["file"] = file

            # remove unrelated data from dictionary before creating Artist
            data.pop('file_type')

            artwork = Artwork(**data)
            artwork.save()            

            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

