"""
URL configuration for djangosqlite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.urls import path


@transaction.atomic()
def create_user(request):
    for _ in User.objects.all()[:10]:
        pass
    random_name = User.objects.make_random_password()
    random_password = User.objects.make_random_password()
    User.objects.create_user(
        username=random_name,
        email=random_name + "@example.com",
        password=random_password,
    )
    return HttpResponse(f"User created, num users: {User.objects.count()}")


urlpatterns = [path("admin/", admin.site.urls), path("create_user/", create_user)]
