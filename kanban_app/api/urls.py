from django.urls import path
from .views import boards_view
# from .views import boards_single_view, email_check_view, tasks_view, tasks_single_view, tasks_comments_view, tasks_comments_single_view, assigned_to_me_view, reviewing_view
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('boards/', boards_view),
    # path('boards/<int:pk>/', boards_single_view, name='boards-detail'),
    # path('email-check/', email_check_view),
    # path('tasks/assigned-to-me/', assigned_to_me_view),
    # path('tasks/reviewing/', reviewing_view),
    # path('tasks/', tasks_view),
    # path('tasks/<int:pk>/', tasks_single_view, name='tasks-detail'),
    # path('tasks/<int:pk>/comments/', tasks_comments_view),
    # path('tasks/<int:pk>/comments/<int:pk>', tasks_comments_single_view, name='tasks-comments-detail')
]