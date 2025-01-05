import os

from django.db import models
from django.contrib.auth.models import AbstractUser

from certificate_generator.settings import BASE_DIR


# Create your models here.

class BaseModel(models.Model):
    class Status(models.IntegerChoices):
        CREATED = 1
        UPDATED = 2
        DELETED = 3
    status = models.IntegerField(choices= Status)
    creation_timestamp = models.DateTimeField(auto_now_add= True)
    updation_timestamp = models.DateTimeField(auto_now= True)
    deletion_timestamp = models.DateTimeField(null= True)

    class Meta:
        abstract= True

class User(AbstractUser, BaseModel):
    username = None
    email = models.CharField(max_length= 60, unique= True)
    middle_name = models.TextField(blank= True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

class UserDocuments(BaseModel):
    def file_path(self, filename):
        return os.path.join(BASE_DIR, "media")
    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    zip_file = models.FilePathField(path= file_path)

    class Meta:
        db_table = "users_zip"

class UserTemplates(BaseModel):
    def name_file(self, filename):
        return os.path.join("templates", f"id-{self.user.id}", filename)

    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    template_file = models.ImageField(upload_to= name_file)

    class Meta:
        db_table = "users_templates"
