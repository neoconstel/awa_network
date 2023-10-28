from django.urls import path

from . import views


urlpatterns = [
    path('artworks/', views.ArtworkList.as_view(), name='artwork_list'),
    path('artwork/<int:pk>/', views.ArtworkDetail.as_view(), name='artwork_detail'),
    path('artists/', views.ArtistList.as_view(), name='artist_list'),
    path('artist/<int:pk>/', views.ArtistDetail.as_view(), name='artist_detail'),
    path('artist/<str:username>/', views.ArtistDetail.as_view(), name='artist_detail'),
]
