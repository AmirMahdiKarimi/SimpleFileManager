from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, GenericAPIView, CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission, DjangoModelPermissions
from django.core.cache import cache
from django.contrib.auth import get_user_model 
from .serializers import CreateUserSerializer, UpdateQoutaSerializer, CreateFileSerializer, RenameFileSerializer,\
        GetAndListFileSerializer, ChangeIsTrashFileSerializer
from .models import CustomUser, File
from .utils import is_unique_name, unique_err_message, owner_err_message


from time import sleep

class CreateUserAPIView(CreateAPIView):
    model = get_user_model()
    serializer_class = CreateUserSerializer


class LogoutAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        request.user.auth_token.delete()
        return Response(data={'message': f"Bye {request.user.username}!"}, status=200)
    
    

class ManagerChangeUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('manager.change_customuser')
    
class UpdateQoutaAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated, ManagerChangeUserPermission, )
    queryset = CustomUser.objects.all()
    serializer_class = UpdateQoutaSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

    def post(self, request, *args, **kwargs):
        lock_id = f"lock:{kwargs['user_id']}"
        locked = cache.add(lock_id, True, timeout=20)
        instance = self.get_object()
        
        if locked:
            try:
                # sleep(30)
                total_qouta = request.data.get('total_qouta')
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                if serializer.is_valid():
                    if total_qouta and instance.used_qouta > int(total_qouta):
                        return Response(data={"message": "total qouta should be greater than used qouta"}, status=402)
                    serializer.save()
                    return Response(data={"message": "total qouta updated successfully"}, status=200)
                else:
                    return Response(data={"message": "invalid input!"}, status=400)
            finally:
                cache.delete(lock_id)
        else:
            return Response(data={"message": "qouta in use."}, status=409)    


class AddFileAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CreateFileSerializer

    def create(self, request, *args, **kwargs):
        lock_id = f"lock:{request.user.id}"
        locked = cache.add(lock_id, True, timeout=20)
        if locked:
            try:
                # sleep(30)
                user = request.user
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                if is_unique_name(serializer.validated_data['name'], user):
                    return unique_err_message()
                file_size = serializer.validated_data['size']
                if user.used_qouta + file_size > user.total_qouta:
                    return Response(data={"message": "you haven't enough qouta for this file."}, status=406)
                user.used_qouta += file_size
                user.save()
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=201, headers=headers)
            finally:
                cache.delete(lock_id)
        else:
            return Response(data={"message": "qouta is updating."}, status=409)    
        
    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class DeleteFileAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, file_id):
        file = get_object_or_404(File, id=file_id)
        if request.user != file.owner:
            return owner_err_message()
        request.user.used_qouta -= file.size
        request.user.save()
        file.delete()
        return Response(data={'message': f"file '{file.name}' delete successfuly."}, status=200)
    

class RenameFileAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all()
    serializer_class = RenameFileSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'file_id'

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user != instance.owner:
            return owner_err_message()
        if is_unique_name(serializer.validated_data['name'], request.user):
            return unique_err_message()
        serializer.save()
        return Response(data={"message": "file renamed successfully."}, status=200)


class ListFileAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetAndListFileSerializer
    
    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)
    

class GetFileAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetAndListFileSerializer
    lookup_url_kwarg = 'file_id'

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)
    

class TrashFileAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeIsTrashFileSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'file_id'

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_trashed == True:
            return Response(data={"message": "this file is in trash."}, status=406)
        instance.is_trashed = True
        instance.save()
        return super().update(request, *args, **kwargs)


class RestoreFileAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeIsTrashFileSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'file_id'

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.is_trashed == False:
            return Response(data={"message": "this file isn't in trash."}, status=406)
        if is_unique_name(instance.name, request.user):
            return unique_err_message()
        instance.is_trashed = False
        instance.save()
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)