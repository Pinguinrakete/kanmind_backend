from kanban_app.models import Boards, Tasks
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import BoardSerializer, TaskSerializer, BoardSingleSerializer

class BoardsView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        boards = Boards.objects.all()
        serializer = BoardSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = BoardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            board = serializer.save()
            return Response(BoardSerializer(board, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardsSingleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        board = Boards.objects.get(pk=pk)
        serializer = BoardSingleSerializer(board, context={'request': request})
        return Response(serializer.data)

#     if request.method == 'GET':
#         boards = Boards.objects.get(pk=pk)
#         board_serializer = BoardSerializer(boards)
#         tasks = Tasks.objects.all()
#         tasks_serializer = TaskSerializer(tasks, many=True, context={'request': request})
#         # return Response(serializer.data)    
#         return Response({
#         "hfgh": board_serializer.data,
#         "tasks": tasks_serializer.data
#     })

#     if request.method == 'PATCH':
#         boards = Boards.objects.get(pk=pk)
#         boards = BoardSerializer(boards)
#         serializer = BoardSerializer(boards, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)


class TasksView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        tasks = Tasks.objects.all()
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)    
    
    def post(self, request):
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
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskSingleView(APIView):
    permission_classes = [AllowAny] 

    def delete(self, request, pk):
        task = Tasks.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        task.delete()
        return Response(serializer.data)
    
    def patch(self, request, pk):
        task = Tasks.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)