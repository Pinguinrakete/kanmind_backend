from kanban_app.models import Boards
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import BoardsSerializer
# from rest_framework import status

@api_view(['GET','POST'])
def boards_view(request):

    if request.method == 'GET':
        boards = Boards.objects.all()
        serializer = BoardsSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BoardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)