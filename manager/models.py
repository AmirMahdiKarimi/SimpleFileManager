from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    total_qouta = models.IntegerField(default=0)
    used_qouta = models.IntegerField(default=0)

    class Meta:
        permissions = (
            ("change_user", "Can change users"),
        )

class File(models.Model):
    name = models.CharField(max_length=60)
    size = models.IntegerField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='files')
    is_trashed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{'(trash)' if self.is_trashed else ''} {self.owner} - {self.name} : {self.size} "

