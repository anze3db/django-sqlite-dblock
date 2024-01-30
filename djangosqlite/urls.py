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
from django.db import connection, transaction
from django.http import HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from basic_model.models import A


def write_to_db():
    A.objects.create()


def read_from_db():
    return list(A.objects.all()[:10])


def read(_):
    return HttpResponse("OK")


@csrf_exempt
def write(_):
    write_to_db()
    return HttpResponse("OK")


@csrf_exempt
def read_write(_):
    read_from_db()
    write_to_db()
    return HttpResponse("OK")


@csrf_exempt
def write_read(_):
    write_to_db()
    read_from_db()
    return HttpResponse("OK")


@transaction.atomic()
def read_transaction(_):
    read_from_db()
    return HttpResponse("OK")


@csrf_exempt
@transaction.atomic()
def write_read_transaction(_):
    write_to_db()
    read_from_db()
    return HttpResponse("OK")


@csrf_exempt
@transaction.atomic()
def read_write_transaction(_):
    read_from_db()
    write_to_db()
    return HttpResponse("OK")


@csrf_exempt
def read_write_transaction_immediate(_):
    connection.cursor().execute("BEGIN IMMEDIATE")
    read_from_db()
    write_to_db()
    connection.cursor().execute("COMMIT")
    return HttpResponse("OK")


urlpatterns = [
    path("read/", read),
    path("write/", write),
    path("read_write/", read_write),
    path("write_read/", write_read),
    path("read_transaction/", read_transaction),
    path("write_read_transaction/", write_read_transaction),
    path("read_write_transaction/", read_write_transaction),
    path("read_write_transaction_immediate/", read_write_transaction_immediate),
]
