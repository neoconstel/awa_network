from django.urls import path

from . import views


urlpatterns = [
    path('artworks/', views.ArtworkList.as_view(), name='artwork_list'),
    path('artwork/<int:pk>/', views.ArtworkDetail.as_view(), name='artwork_detail'),

    path('artists/', views.ArtistList.as_view(), name='artist_list'),
    path('artist/<int:pk>/', views.ArtistDetail.as_view(), name='artist_detail'),
    path('artist/<str:username>/', views.ArtistDetail.as_view(), name='artist_detail'),

    path('art-categories/', views.ArtCategoryList.as_view(), name='art_category_list'),

    path('followings/', views.FollowingList.as_view(), name='following_list'),
    path('following/follow/<str:other_user>/', views.FollowingList.as_view(), name='follow'),
    path('following/unfollow/<str:other_user>/', views.Unfollow.as_view(), name='unfollow'),
    path('following/status/<str:other_user>/', views.FollowingStatus.as_view(), name='following_status'),

    path('react/add/<str:reaction_type_name>/<str:model>/<int:instance_id>/', views.React.as_view(), name='react'),
    path('react/remove/<str:reaction_type_name>/<str:model>/<int:instance_id>/', views.UnReact.as_view(), name='unreact'),
    path('react/list/<str:model>/<int:instance_id>/', views.ReactList.as_view(), name='react_list'),

    path('comments/<str:model>/<int:pk>/', views.CommentList.as_view(), name='comment_list'),
    path('comment/<int:pk>/', views.CommentDetail.as_view(), name='comment_detail'),
    
]
