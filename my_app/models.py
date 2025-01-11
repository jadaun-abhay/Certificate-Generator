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
    permanent_deletion_status = models.BooleanField(default= False)
    starred = models.BooleanField(default= False)

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

class UserFolderStructure(BaseModel):
    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    name = models.TextField()
    parent = models.ForeignKey("self", on_delete= models.SET_NULL, related_name= "child_directories", null= True)

    class Meta:
        db_table = "users_folder_structure"

    def get_directory_path(self, include_self= True):
        path_info = list()
        path_str = str()
        path_dict = {"path_info" : path_info, "path_str" : path_str}
        if include_self:
            path_dict["path_info"].append({"id": self.id, "name": self.name})
            path_dict["path_str"] += self.name + "/"
        for parent in UserFolderStructure.objects.filter(child_directories= self).exclude(status= BaseModel.Status.DELETED):
            result = parent.get_directory_path(include_self= True)
            if len(result) > 0:
                if result:
                    path_dict["path_info"].extend(result["path_info"])
                    path_dict["path_str"] = ''.join([result["path_str"], path_dict["path_str"]])
        return path_dict

class UserZips(BaseModel):
    def zip_path(self, filename):
        return os.path.join(BASE_DIR, "media")
    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    zip_file = models.FilePathField(path= zip_path)
    zip_name = models.TextField()
    parent_directory = models.ForeignKey(UserFolderStructure, on_delete= models.SET_NULL, related_name= "child_zips", null= True)

    class Meta:
        db_table = "users_zips"

class UserTemplates(BaseModel):
    def name_file(self, filename):
        return os.path.join("templates", f"id-{self.user.id}", filename)

    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    parent_directory = models.ForeignKey(UserFolderStructure, on_delete= models.SET_NULL, related_name= "child_templates", null= True)
    template_file = models.ImageField(upload_to= name_file)
    template_name = models.TextField()

    class Meta:
        db_table = "users_templates"

class UserUploads(BaseModel):
    def file_path(self, filename):
        return os.path.join("uploads", f"id-{self.user.id}", filename)

    user = models.ForeignKey(User, on_delete= models.SET_NULL, null= True)
    uploaded_file_path = models.FileField(upload_to= file_path)
    parent_directory = models.ForeignKey(UserFolderStructure, on_delete= models.SET_NULL, related_name= "child_files", null= True)
    uploaded_file_name = models.TextField()

    class Meta:
        db_table = "users_uploads"
