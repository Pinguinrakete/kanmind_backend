from django.urls import path
from .views import BoardsView, BoardsSingleView, TasksView, TaskSingleView
# from .views import email_check_view, tasks_comments_view, tasks_comments_single_view, assigned_to_me_view, reviewing_view

urlpatterns = [
    path('boards/', BoardsView.as_view()),
    path('boards/<int:pk>/', BoardsSingleView.as_view(), name='boards-detail'),
    # path('email-check/', email_check_view),
    # path('tasks/assigned-to-me/', assigned_to_me_view),
    # path('tasks/reviewing/', reviewing_view),
    path('tasks/', TasksView.as_view()),
    path('tasks/<int:pk>/', TaskSingleView.as_view, name='tasks-detail')
    # path('tasks/<int:pk>/comments/', tasks_comments_view),
    # path('tasks/<int:pk>/comments/<int:pk>', tasks_comments_single_view, name='tasks-comments-detail')
]