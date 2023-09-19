from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
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
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            gender=gender
        )
        
        if password:
            user.set_password(password) # encrypts the raw password
            user.save()
        return user
        