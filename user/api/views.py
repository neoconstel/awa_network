# configuration settings
from django.conf import settings

# class-based API views
from rest_framework.views import APIView

# models
from user.models import User, InvalidAccessToken

# serializers
from .serializers import UserSerializer

# response / status
from rest_framework.response import Response
from rest_framework import status

# jwt authentication
from rest_framework_simplejwt.tokens import RefreshToken # new access token
from rest_framework_simplejwt.tokens import AccessToken # verify access token
from rest_framework_simplejwt.exceptions import InvalidToken # exception

# for cryptographic encryption and decryption
from cryptography.fernet import Fernet
encryption_key = settings.CRYPTOGRAPHY_KEY.encode()
encryption_handler = Fernet(encryption_key)

# others
from user.email_sender import send_email


# domain to redirect to from email during email verification, password reset
EMAIL_REDIRECT_DOMAIN = "http://127.0.0.1:8000"


def verify_token(token):
    try:
        access_token = AccessToken(token)
        return access_token.payload
    except InvalidToken:
        return None


# Create your views here.
class Register(APIView):

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.POST)
        data = {}

        if serializer.is_valid():
            new_user = serializer.save()

            # generate jwt access tokens for the new user
            tokens = get_jwt_access_tokens_for_user(new_user)

            data['response'] = 'Registration Successful'
            data['username'] = new_user.username
            data['email'] = new_user.email

            # encrypt access token for sending in verification URL
            encrypted_access_token = \
                encryption_handler.encrypt(tokens['access_token'].encode())

            # send account confirmation email with user verification URL
            send_email(
                'Animation West-Africa Email Verification',
                f'''
                Click this link to activate your awa-network account:
                {EMAIL_REDIRECT_DOMAIN}/auth/verify/?x_access_token={encrypted_access_token.decode()}/
                ''',
                'no-reply@animationwestafrica.com',
                new_user.email
            )


            return Response(data, status=status.HTTP_201_CREATED)

        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class Login(APIView):
    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):

        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        user = User.objects.get(email=email)
        
        if not (user and user.check_password(password)):
            return Response({'status: invalid user'}, status=status.HTTP_400_BAD_REQUEST)

        tokens = get_jwt_access_tokens_for_user(user)

        data = {
            'status': 'logged in',
            'username': user.username
        }

        # create Response, set status/data, add cookies then return response
        response = Response(status=status.HTTP_200_OK)
        response.data = data
        response.set_cookie(
            key='access_token', value=tokens['access_token'], httponly=True)
        response.set_cookie(
            key='refresh_token', value=tokens['refresh_token'], httponly=True)

        return response


class Logout(APIView):
    def post(self, request):
        data = {
                'status': 'logged out'
            }

        response = Response(status=status.HTTP_200_OK)
        response.data = data
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class UserInfo(APIView):
    '''this view was created to test that a user is properly authenticated
    using either the tuple of DEFAULT_AUTHENTICATION_CLASSES specified in
    settings OR via a list of authentication classes specified here (which
    would override the DEFAULT_AUTHENTICATION_CLASSES). If there isn't
    an authenticated user, the returned JSON would have no valid user info.'''

    def get(self, request):

        user = request.user
        data = {
            'username': user.username,
            'user ID': user.id,
            'status': 'authenticated'
        }

        return Response(data, status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    '''when a user clicks the verification link in the email, this is the
    view that handles the verification and subsequent redirection.'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        # the encrypted access token is received here and decoded
        encrypted_access_token = \
            self.request.GET.get('x_access_token').replace('/','').encode()
        access_token = \
            encryption_handler.decrypt(encrypted_access_token).decode()

        token_user_data = verify_token(access_token)
        if token_user_data:
            user = User.objects.get(id=token_user_data['user_id'])
            user.is_active = True
            user.save()
            
            return Response({user.username: "Verified"}, 
                            status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    
class ForgotPassword(APIView):
    '''this view collects the user email and sends an email to it containing
    the url for password reset'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):

        user_email = self.request.POST.get('email')
        user = User.objects.filter(email=user_email).first()
        if user:
        
            # generate fresh jwt access token for user
            access_token = get_jwt_access_tokens_for_user(user)['access_token']

            # encrypt access token for sending in password reset URL
            encrypted_access_token = \
                encryption_handler.encrypt(access_token.encode())

            # send password reset email with user password reset URL
            send_email(
                'AWA-Network Password Reset',
                f'''
                Click this link to reset your AWA-Network password:
                {EMAIL_REDIRECT_DOMAIN}/auth/reset_password/?x_access_token={encrypted_access_token.decode()}/
                ''',
                'no-reply@animationwestafrica.com',
                user_email
            )
            return Response(status=status.HTTP_200_OK)
            
        return Response(
            {"error": "no user with this email exists"},
            status=status.HTTP_404_NOT_FOUND
            )


class ResetPassword(APIView):
    '''when a user clicks the password reset link in the email, this is the
    view that handles the password reset and subsequent redirection.'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    class InvalidAccessToken(Exception):
        pass
    
    def get_user(self):
        # the encrypted access token is received here and decoded
        encrypted_access_token = \
            self.request.GET.get('x_access_token').replace('/','')

        # check/invalidate the encrypted access token to avoid reuse
        invalidated, newly_created = InvalidAccessToken.objects.get_or_create(
                    token=encrypted_access_token)
        if not newly_created:
            raise self.InvalidAccessToken

        encrypted_access_token = encrypted_access_token.encode()
        access_token = \
            encryption_handler.decrypt(encrypted_access_token).decode()

        token_user_data = verify_token(access_token)
        if token_user_data:
            user = User.objects.get(id=token_user_data['user_id'])
            return user
        return None


    def post(self, request):
        password = self.request.POST.get('password')
        password2 = self.request.POST.get('password2')
        try:
            user = self.get_user()
        except self.InvalidAccessToken:
            return Response(
                {"error": "password reset token already used"}, 
                status=status.HTTP_400_BAD_REQUEST)

        if user and password == password2:
            user.set_password(password)
            user.save()
            
            return Response(status=status.HTTP_200_OK)
        
        if not user:
            error = "no user found"
        elif password != password2:
            error = "passwords don't match!"
        return Response(
            {"error": error},
            status=status.HTTP_400_BAD_REQUEST
            )





def get_jwt_access_tokens_for_user(user_instance):
    # generate jwt access tokens for the new user
    refresh_instance = RefreshToken.for_user(user_instance)
    tokens = {
        'refresh_token': str(refresh_instance),
        'access_token': str(refresh_instance.access_token)
    }
    return tokens
