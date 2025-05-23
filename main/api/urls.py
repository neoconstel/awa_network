from django.urls import path

from . import views


urlpatterns = [
    path('artworks/', views.ArtworkList.as_view(), name='artwork_list'),
    path('artwork/<int:pk>/', views.ArtworkDetail.as_view(), name='artwork_detail'),

    path('artists/', views.ArtistList.as_view(), name='artist_list'),
    path('artist/<int:pk>/', views.ArtistDetail.as_view(), name='artist_detail'),
    path('artist/<str:username>/', views.ArtistDetail.as_view(), name='artist_detail'),
    path('artist/profile/save/', views.ArtistProfileSave.as_view(), name='artist_save'),

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
    path('resources/seller/<int:pk>/', views.SellerDetail.as_view(), name='seller_detail'),
    path('resources/seller/<str:alias>/', views.SellerDetail.as_view(), name='seller_detail'),
    path('resources/seller/', views.SellerDetail.as_view(), name='seller_detail'),
    path('resources/product/<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('resources/licenses/', views.LicenseList.as_view(), name='license_list'),
    path('resources/product/list/', views.ListProduct.as_view(), name='list_product'),
    path('resources/product/unlist/', views.UnlistProduct.as_view(), name='unlist_product'),
    path('resources/product/library/add/', views.ProductLibraryAdd.as_view(), name='product_library_add'),
    path('resources/product/library/list/', views.ProductLibraryList.as_view(), name='product_library_list'),
    path('download/product/<int:product_id>/license/<int:license_id>/file/<int:file_id>/', views.ProductDownload.as_view(), name='product_download'),

    path('contests/', views.ContestList.as_view(), name='contest_list'),
    path('contest/<int:pk>/', views.ContestDetail.as_view(), name='contest_detail'),
    path('contest/random/exclude/<int:exclude_id>/', views.RandomContest.as_view(), name='random_contest'),
    
    
    # wagtail admin custom settings API. It may be a good idea to shift this
    # urlpattern along with its view to a separate part.
    path('siteconfigs/', views.SiteConfigurationsApi.as_view(), name='site_configs'),
]
