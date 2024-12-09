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

    path('reviews/', views.ReviewList.as_view(), name='review_list'),
    path('review/<int:pk>/', views.ReviewDetail.as_view(), name='review_detail'),
    path('reviews/pending/', views.PendingReviews.as_view(), name='pending_reviews'),

    path('magazine/articles/', views.ArticleList.as_view(), name='article_list'),
    path('magazine/article/<int:pk>/', views.ArticleDetail.as_view(), name='article_detail'),

    path('resources/categories/', views.ProductCategoryList.as_view(), name='product_category_list'),
    path('resources/products/', views.ProductList.as_view(), name='product_list'),
    path('resources/products/<path:subcategory_path>/', views.ProductList.as_view(), name='product_list_deep'),
    path('resources/sellers/', views.SellerList.as_view(), name='seller_list'),
    
    
    # wagtail admin custom settings API. It may be a good idea to shift this
    # urlpattern along with its view to a separate part.
    path('siteconfigs/', views.SiteConfigurationsApi.as_view(), name='site_configs'),
]
