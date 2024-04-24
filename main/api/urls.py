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
    
]
