from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})

        if User.objects.filter(email=self.validated_data['email']).exists:
            raise serializers.ValidationError({'error': 'Email already exist'})

        account = User(email=self.validated_data['email'], fullname=self.validated_data['fullname'])
        account.set_password(pw)
        account.save()
        return account 



#     fullname = serializers.CharField(write_only=True)
#     email = serializers.EmailField(required=True)

#     def validate(self, data):
#         if data['password'] != data['repeated_password']:
#             raise serializers.ValidationError("Passwords do not match.")
#         validate_password(data['password'])
#         return data

#     def create(self, validated_data):
#         fullname = validated_data.pop('fullname')
#         validated_data.pop('repeated_password')
#         user = User.objects.create_user(
#             username=validated_data['email'], 
#             email=validated_data['email'],
#             password=validated_data['password'],
#             first_name=fullname.split(' ')[0],
#             last_name=' '.join(fullname.split(' ')[1:]),
#         )
#         return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)