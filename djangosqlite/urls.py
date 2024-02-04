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

from basic_model.models import Row


def write_to_db(data):
    Row.objects.create(
        name=data["name"],
        campaign=data["campaign"],
        voice=data["voice"],
        recognize=data["recognize"],
        inside=float(data["inside"]),
        growth=data["growth"],
        side=float(data["side"]),
        yard=data["yard"],
        discussion=data["discussion"],
    )


def read_from_db():
    return list(Row.objects.all()[:10])


@transaction.atomic()
def read_transaction(_):
    read_from_db()
    return HttpResponse("OK")


def read(_):
    read_from_db()
    return HttpResponse("OK")


@csrf_exempt
def write(request):
    write_to_db(request.POST)
    return HttpResponse("OK")


@csrf_exempt
def read_write(request):
    read_from_db()
    write_to_db(request.POST)
    return HttpResponse("OK")


@csrf_exempt
def write_read(request):
    write_to_db(request.POST)
    read_from_db()
    return HttpResponse("OK")


@csrf_exempt
@transaction.atomic()
def write_read_transaction(request):
    write_to_db(request.POST)
    read_from_db()
    return HttpResponse("OK")


@csrf_exempt
@transaction.atomic()
def read_write_transaction(request):
    read_from_db()
    write_to_db(request.POST)
    return HttpResponse("OK")


@csrf_exempt
def read_write_transaction_immediate(request):
    connection.cursor().execute("BEGIN IMMEDIATE")
    read_from_db()
    write_to_db(request.POST)
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
