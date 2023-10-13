from django.shortcuts import render, redirect
import json
from django.conf import settings

# models
from main.models import (Artist, Artwork, File, FileType, ArtCategory)
from user.models import User
from django.contrib.contenttypes.models import ContentType

# serializers
from .serializers import ArtworkSerializer

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
from .permissions import IsAuthenticatedElseReadOnly,IsArtworkAuthorElseReadOnly

# jwt authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.api.views import get_jwt_access_tokens_for_user

# Static/Media
from django.core.files.storage import FileSystemStorage


class ArtworkList(mixins.ListModelMixin, mixins.CreateModelMixin,
                                                generics.GenericAPIView):

    permission_classes = [IsAuthenticatedElseReadOnly]
    # pagination_class = 
    ordering = '-id'

    serializer_class = ArtworkSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        # get dictionary equivalent of POST data and add additional data
        data = request.POST.dict()  # {'title': title, 'content': content,...}
        # data = json.loads(request.body)
        # data['artist'] = self.request.user.artist_instance
        data['category'] = ArtCategory.objects.get(pk=int(data['category']))

        print(f"ORDERED_DICT: {data}\n\n\n")
        print(f"\n\nrequest.FILES: {self.request.FILES['file'].name}\n\n\n")

        serializer = ArtworkSerializer(data=data)

        if serializer.is_valid():
            # create a post instance using the POST data
            artwork = Artwork(**data)
            artwork.save()            

            valid_data = serializer.data

            # image upload
            # request_file_object = request.FILES['file']
            # file_storage = FileSystemStorage()
            # file_name = str(request_file_object).split('.')[0]
            # stored_file = file_storage.save(file_name, request_file_object)
            # file_url = file_storage.url(stored_file)
            # valid_data["file"] = {"url": file_url}

            from django.core.files import File as DjangoFile

            # with open('/path/to/existing_file.txt') as f:
            wrapped_file = DjangoFile(request.FILES['file'])
            m = File(resource=wrapped_file)
            m.save()
            valid_data["file"] = {"url": m.url}

            return Response(valid_data, status=status.HTTP_201_CREATED)
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
            elif filter == 'author':
                filtered_query = Artwork.objects.filter(
                        user__username__istartswith=search_term).all()
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
