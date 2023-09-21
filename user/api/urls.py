from django.urls import path

from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user_info/',views.UserInfo.as_view(),name='user_info'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),	
    path('register/', views.Register.as_view(), name="register"),
    path('verify/', views.VerifyEmail.as_view(), name="verify_email"),
    path('forgot_password/', views.ForgotPassword.as_view(), name="forgot_password"),
    path('reset_password/', views.ResetPassword.as_view(), name="reset_password")
]
