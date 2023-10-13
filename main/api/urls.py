from django.urls import path

from . import views


urlpatterns = [
    path('artworks/', views.ArtworkList.as_view(), name='artwork_list'),
    path('artwork/<int:pk>/', views.ArtworkDetail.as_view(), name='artwork_detail'),
]
