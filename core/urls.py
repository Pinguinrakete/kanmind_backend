"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

"""
Main URL configuration for the Django project.

Endpoints:

- /admin/  
  Django admin interface.

- /api-auth/  
  Django REST Framework's built-in authentication views (login/logout).

- /api/  
  Includes URLs from the 'auth_app' application (user registration, login, etc.).

- /api/  
  Includes URLs from the 'kanban_app' application (boards, tasks, comments, etc.).

Note: Both 'auth_app' and 'kanban_app' APIs are mounted under the same /api/ prefix.
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth', include('rest_framework.urls')),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('kanban_app.api.urls'))
]