# configuration settings
from django.conf import settings

# class-based API views
from rest_framework.views import APIView

# models
from user.models import User, InvalidAccessToken
from django.db.models import Q

# serializers
from .serializers import UserSerializer, UserReadOnlySerializer

# response / status
from rest_framework.response import Response
from rest_framework import status

# jwt authentication
from rest_framework_simplejwt.tokens import RefreshToken # new access token
from rest_framework_simplejwt.tokens import AccessToken # verify access token
from rest_framework_simplejwt.exceptions import InvalidToken # exception

# for cryptographic encryption and decryption
import cryptography
from cryptography.fernet import Fernet
encryption_key = settings.CRYPTOGRAPHY_KEY.encode()
encryption_handler = Fernet(encryption_key)

# others
import json
from user.email_scripts.emailjs import send_email
from datetime import datetime, timedelta
from django.contrib.auth import login


# frontend URL to redirect to from email during email verification
VERIFY_REDIRECT_URL = f"{settings.CLIENT_DOMAIN}/verify_email"

# frontend URL to redirect to from email during password reset
RESET_REDIRECT_URL = f"{settings.CLIENT_DOMAIN}/reset_password"


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
        serializer = UserSerializer(data=json.loads(request.body))
        data = {}

        if serializer.is_valid():
            new_user = serializer.save()

            # TEMPORARY CODE TILL EMAIL SENDING FEATURE WORKS FOR VERIFICATION
            new_user.is_active = True
            new_user.save()

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
                {VERIFY_REDIRECT_URL}/?xtoken={encrypted_access_token.decode()}/
                ''',
                new_user.email
            )

            return Response(data, status=status.HTTP_200_OK)

        # get the topmost error in string form from every validation error
        data['error'] = serializer.errors[list(serializer.errors)[0]][0]

        return Response (data, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class Login(APIView):
    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        body = json.loads(request.body)
        user_login = body.get('username')
        password = body.get('password')
        remember_me = body.get('rememberMe')

        user = User.objects.filter(
            Q(email=user_login)|Q(username=user_login)).first()
        
        # invalid or inactive user
        if not (user and user.check_password(password) and user.is_active):
            if user and user.check_password(password):
                return Response(
                {
                    'error': 'inactive user'
                },
                status=status.HTTP_400_BAD_REQUEST)

            return Response(
            {
                'error': 'invalid user'
            },
            status=status.HTTP_400_BAD_REQUEST)


        # FOUND VALID, ACTIVE USER SO PROCEED WITH LOGIN PROCESS

        # -----session auth (useful for 'don't remember me' login)------
        '''saves a session cookie containing sessionid. Expires after 2 weeks
        by default, unless SESSION_EXPIRE_AT_BROWSER_CLOSE = True is set in
        settings.py in which case it gets deleted once browser is closed.'''
        login(request, user)

        # -----JWT auth (via persistently saved authentication cookies)-----
        tokens = get_jwt_access_tokens_for_user(user)

        data = {
            'status': 'logged in',
            'user': UserReadOnlySerializer(user).data
        }

        # Create a datetime object for one year in the future
        expires = datetime.utcnow() + timedelta(days=365)

        # create Response, set status/data, add JWT cookies and return response
        response = Response(status=status.HTTP_200_OK)
        response.data = data
        if remember_me:
            response.set_cookie(
                key='access_token', value=tokens['access_token'], 
                httponly=True, expires=expires)
            response.set_cookie(
                key='refresh_token', value=tokens['refresh_token'], 
                httponly=True, expires=expires)          

        return response


class Logout(APIView):
    def post(self, request):
        data = {
                'status': 'logged out'
            }

        response = Response(status=status.HTTP_200_OK)
        response.data = data

        # delete jwt cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        # delete session cookies
        response.delete_cookie('csrftoken')
        response.delete_cookie('sessionid')

        print("logged out")
        return response


class UserInfo(APIView):
    '''this view was created to test that a user is properly authenticated
    using either the tuple of DEFAULT_AUTHENTICATION_CLASSES specified in
    settings OR via a list of authentication classes specified here (which
    would override the DEFAULT_AUTHENTICATION_CLASSES). If there isn't
    an authenticated user, the returned JSON would have no valid user info.'''

    def get(self, request):

        user = request.user
        login_status = 'authenticated' if request.user else 'anonymous'
        data = {
            'username': user.username,
            'userID': user.id,
            'status': login_status
        }

        return Response(data, status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    '''when a user clicks the verification link in the email and gets directed
    to the frontend, the frontend calls this view to handle the verification.'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):

        body = json.loads(request.body)

        # the encrypted access token is received here and decoded
        encrypted_access_token = \
            body.get('x_access_token').replace('/','').encode()
        
        try:
            access_token = \
                encryption_handler.decrypt(encrypted_access_token).decode()
        except:
            return Response({
                'xtoken': encrypted_access_token,
                'error': "invalid verification token"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        token_user_data = verify_token(access_token)
        if token_user_data:
            user = User.objects.get(id=token_user_data['user_id'])
            user.is_active = True
            user.is_verified = True
            user.save()
            
            return Response({"verified_user": user.username}, 
                            status=status.HTTP_200_OK)
        return Response({
            'xtoken': encrypted_access_token,
            'error': "invalid verification token"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    
class ForgotPassword(APIView):
    '''this view collects the user email from the frontend and sends an email 
    containing the url for password reset. The url leads to the frontend's
    password reset page'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    def post(self, request):

        body = json.loads(request.body)
        user_email = body.get('email')
        user = User.objects.filter(email=user_email).first()
        if user:
        
            # generate fresh jwt access token for user
            access_token = get_jwt_access_tokens_for_user(user)['access_token']

            # encrypt access token for sending in password reset URL
            encrypted_access_token = \
                encryption_handler.encrypt(access_token.encode())

            print(f"\n\n{encrypted_access_token.decode()}\n\n")

            # send password reset email with user password reset URL
            send_email(
                'AWA-Network Password Reset',
                f'''
                Click this link to reset your AWA-Network password:
                {RESET_REDIRECT_URL}/?xtoken={encrypted_access_token.decode()}/
                ''',
                user_email
            )
            return Response(
                {'status': 'reset email sent'},status=status.HTTP_200_OK)
            
        return Response(
            {"error": "no user with this email exists"},
            status=status.HTTP_404_NOT_FOUND
            )


class ResetPassword(APIView):
    '''when a user clicks the password reset link in the email, they get
    directed to the frontend password reset page containing a password reset
    form which is authorized by the encrypted token in the url. On submission
    of that form, this is the view which handles the password reset.'''

    # exempt this view from requiring authentication/permissions
    permission_classes = []
    authentication_classes = []

    class InvalidAccessToken(Exception):
        pass
    
    def get_user(self):
        body = json.loads(self.request.body)

        # the encrypted access token is received here and decoded
        encrypted_access_token = \
            body.get('x_access_token').replace('/','')

        # check if encrypted access token is invalidated, to avoid reuse
        invalidated_token = InvalidAccessToken.objects.filter(
                    token=encrypted_access_token).first()
        if invalidated_token:
            raise self.InvalidAccessToken

        encrypted_access_token = encrypted_access_token.encode()
        access_token = \
            encryption_handler.decrypt(encrypted_access_token).decode()

        token_user_data = verify_token(access_token)
        if token_user_data:
            user = User.objects.get(id=token_user_data['user_id'])
            return user, encrypted_access_token.decode()
        return None


    def post(self, request):
        body = json.loads(self.request.body)

        password = body.get('password')
        password2 = body.get('password2')
        
        try:
            user, encrypted_access_token = self.get_user()
        except self.InvalidAccessToken:
            return Response(
                {"error": "password reset token already used"}, 
                status=status.HTTP_400_BAD_REQUEST)
        except cryptography.fernet.InvalidToken:
            return Response(
                {"error": "invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST)

        if user:

            try:
                assert password == password2
                assert len(password.strip()) >= 1
            except:
                return Response({
                    "error": "passwords must not be blank and must match"},
                status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(password)
            user.save()

            # invalidate access token on successful reset to avoid reuse
            inv = InvalidAccessToken.objects.create(
                token=encrypted_access_token)
            inv.save()
            
            return Response({
                'status': 'reset password ok', 
                'user': user.username},status=status.HTTP_200_OK)
        
        # no user
        else:
            return Response({"error": "no user found"},
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