from django.urls import path
from .views import BoardsView, BoardsSingleView, EmailCheckView, AssignedToMeView, ReviewingTasksView, TasksView, TaskSingleView, TaskCommentsView, TasksCommentsSingleView

"""
URL patterns for the project API endpoints.

Endpoints:

- GET, POST /boards/  
  Manage boards list and create new boards (BoardsView).

- GET, PATCH, DELETE /boards/{pk}/  
  Retrieve, update, or delete a specific board (BoardsSingleView).

- GET /email-check/?email={email}  
  Check if a user with the given email exists (EmailCheckView).

- GET /tasks/assigned-to-me/  
  List tasks assigned to the authenticated user (AssignedToMeView).

- GET /tasks/reviewing/  
  List tasks where the authenticated user is the reviewer (ReviewingTasksView).

- POST /tasks/  
  Create a new task in a board (TasksView).

- GET, PATCH, DELETE /tasks/{task_id}/  
  Retrieve, update, or delete a specific task (TaskSingleView).

- GET, POST /tasks/{task_id}/comments/  
  Retrieve or add comments on a specific task (TaskCommentsView).

- DELETE /tasks/{task_id}/comments/{comment_id}  
  Delete a specific comment on a task (TasksCommentsSingleView).
"""
urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardsSingleView.as_view(), name='boards-detail'),
    path('email-check/', EmailCheckView.as_view()),
    path('tasks/assigned-to-me/', AssignedToMeView.as_view()),
    path('tasks/reviewing/', ReviewingTasksView.as_view()),
    path('tasks/', TasksView.as_view()),
    path('tasks/<int:task_id>/', TaskSingleView.as_view(), name='tasks-detail'),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view()),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TasksCommentsSingleView.as_view(), name='tasks-comments-detail')
]