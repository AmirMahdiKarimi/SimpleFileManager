from rest_framework.response import Response 
from .models import File


def is_unique_name(name, user):
    if File.objects.filter(name=name, owner=user, is_trashed=False).exists():
        return True
    return False

def unique_err_message():
    return Response(data={"message": "Name must be unique for exists objects."}, status=400)

def owner_err_message():
    return Response(data={"message": "you haven't this file!"}, status=403) 
