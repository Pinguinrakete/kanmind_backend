from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from kanban_app.models import Boards, Tasks, Comments
from .permissions import IsBoardMemberOrOwner, IsMemberOfTasksBoard, IsCommentAuthor
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import BoardSerializer, BoardPatchSerializer, BoardSingleSerializer, TaskSerializer, TaskReviewingAndAssignedToMeSerializer, CommentSerializer

class BoardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boards = Boards.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
        serializer = BoardSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = BoardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            board = serializer.save()
            return Response(BoardSerializer(board, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardsSingleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            board = Boards.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct().get(pk=pk)
        except Boards.DoesNotExist:
            return Response({"detail": "Board not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoardSingleSerializer(board, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            board = Boards.objects.filter(Q(owner=request.user) | Q(members=request.user)).distinct().get(pk=pk)
        except Boards.DoesNotExist:
            return Response({"detail": "Board not found or not authorized."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoardPatchSerializer(board, data=request.data, partial=True, context={'request': request})  
        if serializer.is_valid():
            board = serializer.save()
            return Response(BoardPatchSerializer(board, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            board = Boards.objects.get(pk=pk)
        except Boards.DoesNotExist:
            return Response({"detail": "Board not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user != board.owner:
            return Response({"detail": "Only the owner can delete this board."}, status=status.HTTP_403_FORBIDDEN)

        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
            email = request.query_params.get('email')
            if not email:
                return Response({'detail': 'Email query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email__iexact=email)
                return Response({
                    'id': user.id,
                    'email': user.email,
                    'fullname': f"{user.first_name} {user.last_name}".strip(),
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class AssignedToMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignedTasks = Tasks.objects.filter(assignee=request.user)
        serializer = TaskReviewingAndAssignedToMeSerializer(assignedTasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviewingTasks = Tasks.objects.filter(reviewer=request.user)
        serializer = TaskReviewingAndAssignedToMeSerializer(reviewingTasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TasksView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
            board_id = request.data.get('board')
            if not board_id:
                return Response({"error": "Board-ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                board = Boards.objects.get(id=board_id)
            except Boards.DoesNotExist:
                return Response({"error": "Board does not exist."}, status=status.HTTP_404_NOT_FOUND)

            if request.user != board.owner and request.user not in board.members.all():
                return Response({"error": "Access denied. You are not a member of this board."},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = TaskSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                task = serializer.save()
                return Response(TaskSerializer(task, context={'request': request}).data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TaskSingleView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 

    def delete(self, request, task_id):
        task = Tasks.objects.get(pk=task_id)

        isTaskCreator = task.createdBy == request.user
        isBoardOwner = task.board.owner == request.user

        if not (isTaskCreator or isBoardOwner):
            raise PermissionDenied("You are not allowed to delete this task.")
        
        serializer = TaskSerializer(task)
        task.delete()
        return Response(serializer.data)
    
    def patch(self, request, task_id):
            try:
                task = Tasks.objects.get(pk=task_id)
            except Tasks.DoesNotExist:
                return Response({"detail": "Task not found."}, status=404)

            if request.user not in task.board.members.all():
                raise PermissionDenied("You are not a member of this board and are not allowed to work on this task.")

            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
            

class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfTasksBoard] 

    def get(self, request, task_id):
        task = get_object_or_404(Tasks, id=task_id)
        self.check_object_permissions(request, task)

        comments = task.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = get_object_or_404(Tasks, id=task_id)
        self.check_object_permissions(request, task)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TasksCommentsSingleView(APIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, task_id, comment_id):
        task = get_object_or_404(Tasks, id=task_id)

        comment = get_object_or_404(Comments, id=comment_id, task=task)
        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)