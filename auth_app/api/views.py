from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer

""" 
This handles the user registration. 

Method: POST
Accepts: full name, email, password, repeated password.
Returns: user data on success or validation errors.
"""
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, create = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'fullname': f"{saved_account.first_name} {saved_account.last_name}".strip(),
                'email': saved_account.email,
                'user_id': saved_account.id
            }
        else:
            data=serializer.errors

        return Response(data, status=status.HTTP_201_CREATED)

"""
This handles the user login.

Method: POST
Accepts: email and password.
Returns: user data on success or authentication error.
"""
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            login_user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=login_user)
            data = {
                'token': token.key,
                'fullname': f"{login_user.first_name} {login_user.last_name}".strip(),
                'email': login_user.email,
                'user_id': login_user.id
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)