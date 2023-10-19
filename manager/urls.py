from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    path('user/login/', view=obtain_auth_token),
    path('user/register/', views.CreateUserAPIView.as_view()),
    path('user/logout/', views.LogoutAPIView.as_view()),
    path('user/update_qouta/<int:user_id>/', views.UpdateQoutaAPIView.as_view()),
    path('file/add/', views.AddFileAPIView.as_view()),
    path('file/delete/<int:file_id>/', views.DeleteFileAPIView.as_view()),
    path('file/rename/<int:file_id>/', views.RenameFileAPIView.as_view()),
    path('file/list/', views.ListFileAPIView.as_view()),
    path('file/get/<int:file_id>/', views.GetFileAPIView.as_view()),
    path('file/trash/<int:file_id>/', views.TrashFileAPIView.as_view()),
    path('file/restore/<int:file_id>/', views.RestoreFileAPIView.as_view()),
]
