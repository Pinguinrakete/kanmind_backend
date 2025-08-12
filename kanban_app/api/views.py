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

"""
This handles retrieving all boards the user is involved in and creating new boards.

Method:  
- GET: Returns all boards where the user is the owner or a member.  
- POST: Creates a new board.

GET Request:  
Returns a list of boards, each with:  
- board ID  
- title  
- member count  
- ticket count  
- tasks to do count  
- high priority tasks count  
- owner ID

POST Request:  
Accepts:  
- title (string)  
- members (optional list of user IDs)

Returns on success (201):  
- full board data as described above  
Returns on error (400):  
- validation errors

Permissions:  
- User must be authenticated.
"""
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

"""
This handles retrieving, updating, and deleting a single board.

Permissions:  
- User must be authenticated.  
- Access limited to boards where the user is owner or member.  
- Only the owner can delete the board.

Methods:

GET /boards/{pk}/  
- Returns detailed information about the specified board.  
- Returns 401 if not authenticated.  
- Returns 404 if board does not exist or access is denied.

PATCH /boards/{pk}/  
- Accepts partial updates: title and members.  
- Updates the specified board if user is owner or member.  
- Returns updated board data on success.  
- Returns 404 if board not found or no access.  
- Returns 400 on validation errors.

DELETE /boards/{pk}/  
- Deletes the specified board.  
- Only the owner can delete.  
- Returns 403 if user is not the owner.  
- Returns 404 if board not found.  
- Returns 204 on successful deletion.
"""
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
        
        if 'members' in serializer.errors:
            return Response(
                {"detail": "Invalid request data. Some users may be invalid."}, status=status.HTTP_400_BAD_REQUEST)

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

"""
This handles checking if a user with a given email exists.

Method: GET  
Query Parameters:  
- email (string, required): The email address to check.

Returns:  
- 200 OK with user data (ID, email, full name) if a user with the given email exists.  
- 400 Bad Request if the 'email' query parameter is missing.  
- 404 Not Found if no user with the specified email exists.

Permissions:  
- User must be authenticated.
"""
class AssignedToMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignedTasks = Tasks.objects.filter(assignee=request.user)
        serializer = TaskReviewingAndAssignedToMeSerializer(assignedTasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
"""
This returns all tasks where the authenticated user is the reviewer.

Method: GET  
Returns:  
- List of tasks assigned to the user as reviewer, including:  
  - task ID  
  - board ID  
  - title  
  - description  
  - status  
  - priority  
  - assignee (user info)  
  - reviewer (user info)  
  - due_date  
  - comments_count

Permissions:  
- User must be authenticated.
"""
class ReviewingTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviewingTasks = Tasks.objects.filter(reviewer=request.user)
        serializer = TaskReviewingAndAssignedToMeSerializer(reviewingTasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

"""
This handles creating a new task within a board.

Method: POST  
Accepts:  
- board (ID of the board to which the task belongs) [required]  
- title (string)  
- description (string)  
- status (string)  
- priority (string/int)  
- assignee_id (user ID)  
- reviewer_id (user ID)  
- due_date (datetime)

Returns:  
- 201 Created with full task data on success  
- 400 Bad Request if board ID is missing or validation fails  
- 403 Forbidden if the user is not a member or owner of the board  
- 404 Not Found if the board does not exist

Permissions:  
- User must be authenticated.  
- User must be the board owner or a member to create tasks.
"""
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


"""
This handles retrieving, updating, and deleting a single task.

Permissions:  
- User must be authenticated.  
- User must be the task creator or board owner to delete the task.  
- User must be a board member to update the task.

Methods:

DELETE /tasks/{task_id}/  
- Deletes the specified task if the user is the creator or board owner.  
- Returns the deleted task data on success.  
- Raises PermissionDenied if the user is not authorized.

PATCH /tasks/{task_id}/  
- Partially updates the specified task.  
- Returns updated task data on success.  
- Returns 404 if the task is not found.  
- Raises PermissionDenied if the user is not a member of the board.  
- Returns 400 on validation errors.
"""
class TaskSingleView(APIView):
    permission_classes = [IsAuthenticated]

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
            
"""
This handles retrieving and creating comments on a specific task.

Permissions:  
- User must be authenticated.  
- User must be a member of the task's board (checked via IsMemberOfTasksBoard permission).

Methods:

GET /tasks/{task_id}/comments/  
- Returns all comments for the specified task, ordered by newest first.  
- Each comment includes ID, created_at timestamp, author (full name or username), and content.

POST /tasks/{task_id}/comments/  
- Accepts:  
  - content (string)  
- Creates a new comment on the specified task with the authenticated user as author.  
- Returns the created comment data on success (201).  
- Returns 400 on validation errors.

Raises 404 if the task does not exist or 403 if permission check fails.
"""
class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfTasksBoard] 

    def get(self, request, task_id):
        task = get_object_or_404(Tasks, id=task_id)
        self.check_object_permissions(request, task)

        comments = task.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        task = get_object_or_404(Tasks, id=task_id)
        self.check_object_permissions(request, task)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
"""
This handles deleting a single comment on a task.

Permissions:  
- User must be authenticated.  
- User must be the author of the comment (checked via IsCommentAuthor permission).

Method:

DELETE /tasks/{task_id}/comments/{comment_id}/  
- Deletes the specified comment on the specified task.  
- Returns 204 No Content on successful deletion.  
- Returns 404 if the task or comment does not exist.  
- Returns 403 if the user is not the comment author.

"""
class TasksCommentsSingleView(APIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, task_id, comment_id):
        task = get_object_or_404(Tasks, id=task_id)
        comment = get_object_or_404(Comments, id=comment_id, task=task)
        self.check_object_permissions(request, comment)

        comment.delete()

        task.comments_count = task.comments.count()
        task.save(update_fields=['comments_count'])
        
        return Response(status=status.HTTP_204_NO_CONTENT)