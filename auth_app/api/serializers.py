from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        fullname = self.validated_data['fullname']
        email = self.validated_data['email']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': 'Email already exists'})

        name_parts = fullname.strip().split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        user = User(
            email=email,
            username=email, 
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(pw)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        
        data['user'] = user
        return data