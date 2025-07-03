from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, EmailAuthTokenSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
                try:
                    user = serializer.save()
                    token, _ = Token.objects.get_or_create(user=user)
                    data = {
                        'token': token.key,
                        'fullname': f"{user.first_name} {user.last_name}".strip(),
                        'email': user.email,
                        'user_id': user.id
                    }
                    return Response(data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response(
                        {"error": "Internal Server Error", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key, 
            'email': user.email
        })