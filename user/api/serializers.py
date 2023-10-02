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
        