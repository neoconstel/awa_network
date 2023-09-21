from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationViaCookies(JWTAuthentication):
    '''This class is a MODIFIED version of the JWTAuthentication class, and
    is set to authenticate a user via JWT access_token stored in the browser 
    COOKIES (after a previous login). It differs from the default 
    JWTAuthentication class which uses the access_token passed directly into
    the request HEADER as bearer token'''
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token is None:
            return None

        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)

        return (user, validated_token)
