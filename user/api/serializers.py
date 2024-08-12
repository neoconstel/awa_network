from rest_framework import serializers
from rest_framework.serializers import ValidationError

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    # custom serializer field
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = '__all__'


    # Custom validation, which determines the output of serizer.is_valid() in
    # the view. The keys (e.g password2 in data['password2]) must
    # be the names of existing serializer fields, whether provided from the
    # model by default (password) or customly added in the serializer
    # class (password2)
    def validate(self, data):
        # check equality of passwords
        if data['password'] != data['password2']:
            raise ValidationError("passwords should match!")
        return super().validate(data)

    
    # by default, the serializer.save() saves a user instance with the password
    # in raw text. So we use a custom serializer save() method to ensure that
    # the password for the user instance is saved correctly and encrypted.
    def save(self, **kwargs):
        
        email = self.validated_data.get('email')
        username = self.validated_data.get('username')
        first_name = self.validated_data.get('first_name')
        last_name = self.validated_data.get('last_name')
        gender = self.validated_data.get('gender')
        password = self.validated_data.get('password') # raw text password

        # custom validations            
        if User.objects.filter(email=email).exists():
            raise ValidationError({'error': 'Email already exists!'})

        # no issues, so proceed to create User account manually
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            gender=gender
        )
 
        user.set_password(password) # encrypts the raw password
        user.save()
        return user


class UserReadOnlySerializer(UserSerializer):
    '''this class is intended for use in other serializers which depend on the
    user model, most especially in the case of serializer nesting. For example, 
    an ArtistSerializer needs to nest the UserSerializer while hiding 
    confidential info. To do that, confidential fields have been excluded here.
    The save() method has also been overridden to ensure that this "ReadOnly" 
    version of the UserSerializer class cannot be used to manipulate 
    the database.
    
    Another suitable use is to return user public info on login. Just serialize
    the authenticated user instance with this, and return the data which is
    safe for storing on the browser.'''
    # custom serializer field
    name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    # custom serializer field method to get property
    # syntax: get_<custom serializer field name>
    def get_name(self, object):
        return f'{object.first_name} {object.last_name}'
    
    def get_groups(self, object):
        group_names = list(map(lambda group:group.name,object.groups.all()))
        return group_names

    class Meta:
        model = UserSerializer.Meta.model
        exclude = ['email','password'] # hide confidential info when read
        
    # make this class unable to write to database (readonly)
    def save():
        pass
    