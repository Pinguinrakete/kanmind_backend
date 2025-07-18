from django.urls import path
from .views import BoardsView, BoardsSingleView, EmailCheckView, AssignedToMeView, ReviewingTasksView, TasksView, TaskSingleView, TaskCommentsView, TasksCommentsSingleView

urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardsSingleView.as_view(), name='boards-detail'),
    path('email-check/', EmailCheckView.as_view()),
    path('tasks/assigned-to-me/', AssignedToMeView.as_view()),
    path('tasks/reviewing/', ReviewingTasksView.as_view()),
    path('tasks/', TasksView.as_view()),
    path('tasks/<int:task_id>/', TaskSingleView.as_view(), name='tasks-detail'),
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view()),
    path('tasks/<int:task_id>/comments/<int:comment_id>', TasksCommentsSingleView.as_view(), name='tasks-comments-detail')
]