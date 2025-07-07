from kanban_app.models import Boards, Tasks
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import BoardSerializer, TaskSerializer

@api_view(['GET','POST'])
@permission_classes([AllowAny])
# @permission_classes([IsAuthenticated])  # Wird später noch angepaßt
def boards_view(request):

    if request.method == 'GET':
        boards = Boards.objects.all()
        serializer = BoardSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = BoardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            board = serializer.save()
            return Response(BoardSerializer(board).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH'])
@permission_classes([AllowAny])
def boards_single_view(request, pk):

    if request.method == 'GET':
        boards = Boards.objects.get(pk=pk)
        board_serializer = BoardSerializer(boards)
        tasks = Tasks.objects.all()
        tasks_serializer = TaskSerializer(tasks, many=True, context={'request': request})
        # return Response(serializer.data)    
        return Response({
        "hfgh": board_serializer.data,
        "tasks": tasks_serializer.data
    })

    if request.method == 'PATCH':
        boards = Boards.objects.get(pk=pk)
        boards = BoardSerializer(boards)
        serializer = BoardSerializer(boards, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def tasks_view(request):

    if request.method == 'GET':
        tasks = Tasks.objects.all()
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)    
    
    if request.method == 'POST':
        queryset = Tasks.objects.all()
        serializer = TaskSerializer(queryset, many=True, context={'request': request})

        def create(self, request, *args, **kwargs):
            data = request.data.copy()

            assignee_id = data.get('assignee')
            reviewer_id = data.get('reviewer')

            task = Tasks.objects.create(
                board_id=data.get('board'),
                title=data.get('title'),
                description=data.get('description', ''),
                status=data.get('status', 'to-do'),
                priority=data.get('priority', 'medium'),
                assignee_id=assignee_id,
                reviewer_id=reviewer_id,
                due_date=data.get('due_date')
            )
            serializer = self.serializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE','PATCH'])
@permission_classes([AllowAny])
def tasks_single_view(request, pk):

    if request.method == 'DELETE':
        task = Tasks.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        task.delete()
        return Response(serializer.data)
    
    if request.method == 'PATCH':
        task = Tasks.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)