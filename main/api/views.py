from django.shortcuts import render, redirect
import json
from django.conf import settings

# models
from main.models import (
    Artist, Artwork, File, FileType, FileGroup, ArtCategory, Image, Following,
    ReactionType, Reaction, ViewLog, Comment)
from user.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

# serializers
from .serializers import (
    ArtworkSerializer, ArtistSerializer, ArtCategorySerializer,
    FollowingSerializer, ReactionSerializer, CommentSerializer)

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
IsArtworkAuthorElseReadOnly,IsArtistUserElseReadOnly,
IsCommentAuthorElseReadOnly)

# jwt authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.api.views import get_jwt_access_tokens_for_user

# File handling
from django.core.files import File as DjangoFile

# pagination
from .pagination import (ArtworkPaginationConfig, ArtistPaginationConfig,
FollowPaginationConfig, ReactionPaginationConfig, CommentPaginationConfig)


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
        '''general rule to retain logical coherence:
        - valid terms pass through a query filter() method
        - invalid terms return an empty queryset ( ModelName.objects.none() )'''

        # get the search term submitted with GET
        search_term = self.request.GET.get('search')
        filter = self.request.GET.get('filter')

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

        if self.request.user.is_authenticated:
            reactions_by_user = Reaction.objects.filter(content_type=content_type, 
                            object_id=instance_id, user=request.user).order_by(
                                self.__class__.ordering).all()
            user_reactions_serialized = ReactionSerializer(reactions_by_user, many=True)

            user_reaction_names = [
                reaction['reaction_type'] for reaction in user_reactions_serialized.data]
            response.data['user_reactions'] = user_reaction_names

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
    ordering = 'id'

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
                if parent_comment.post.pk != post.pk:
                    raise CommentNotForPost
            else:
                parent_comment = None
            content = self.request.GET.get('content')
        except Comment.DoesNotExist:
            return Response({"error": "invalid parent_comment id"}, 
                                            status=status.HTTP_404_NOT_FOUND)
        except CommentNotForPost:
            return Response(
                {"error": f"post (id={post_id}) and parent_comment (post_id={parent_comment.post.pk}) do not match!"},
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
