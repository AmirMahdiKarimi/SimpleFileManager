from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import File


UserModel = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ( "id", "username", "password", )

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user


class UpdateQoutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'total_qouta', )

    def update(self, instance, validated_data):
        instance.total_qouta = validated_data.get('total_qouta', instance.total_qouta)
        instance.save()
        return instance
    

class CreateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('name', 'size', 'owner', )
        read_only_fields = ('owner',)
    

class RenameFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'name', )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class GetAndListFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'name', 'size', 'is_trashed')


class ChangeIsTrashFileSerializer(GetAndListFileSerializer):
    class Meta:
        read_only_fields = ('name', 'size', 'is_trashed', )

